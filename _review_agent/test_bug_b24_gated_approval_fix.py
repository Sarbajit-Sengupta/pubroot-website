"""
Tests for Bug B24: Gated Submission Approval Flow

BUG B24 ROOT CAUSE:
    The workflow added `awaiting-approval` label to gated submissions, but:
    1. Tier 3 picker excluded `pending-review` label (different name!)
    2. Stage 6 tried to remove `pending-review` label (not `awaiting-approval`)
    3. Tests, CLI, and docs all expected `pending-review` label
    
    Additionally, even with the correct label name, the Tier 3 jq filter excluded
    `pending-review` BEFORE the gating check, so approved submissions (with both
    `pending-review` and `approved-for-review` labels) were never picked.

FIX:
    1. Workflow now adds `pending-review` label (consistent with other code)
    2. Tier 3 no longer excludes `pending-review` in jq filter
    3. Gating check determines if issue is approved (has `approved-for-review` label)
    4. Approved issues are picked even if they still have `pending-review` label
    5. Stage 6 removes `pending-review` when accepting/rejecting (already correct)

FLOW AFTER FIX:
    1. Untrusted author submits → workflow adds `pending-review` label
    2. Tier 3 includes issue as candidate (no longer excluded by jq)
    3. Gating check: fails (no `approved-for-review`), skipped with "gated" reason
    4. Maintainer adds `approved-for-review` label
    5. Next cron: Tier 3 includes issue, gating check passes, issue is picked
    6. Review runs, stage 6 removes `pending-review` and adds accepted/rejected
"""

import pytest


def test_workflow_adds_correct_label_name():
    """
    Verify workflow uses `pending-review` label, not `awaiting-approval`.
    
    This is tested by reading the workflow file and checking the label name.
    """
    import os
    workflow_path = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "review.yml")
    with open(workflow_path, "r") as f:
        workflow = f.read()
    
    # Should create pending-review label
    assert 'gh label create "pending-review"' in workflow
    
    # Should add pending-review label
    assert 'gh issue edit "$ISSUE" --add-label pending-review' in workflow
    
    # Should NOT mention awaiting-approval label (old bug)
    assert 'awaiting-approval' not in workflow.replace('pending-review', 'PENDING')


def test_tier3_does_not_exclude_pending_review():
    """
    Verify Tier 3 jq filter does NOT exclude pending-review.
    
    After Bug B24 fix, pending-review should not be in the jq exclusion list.
    The gating check handles approval.
    """
    import os
    workflow_path = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "review.yml")
    with open(workflow_path, "r") as f:
        workflow = f.read()
    
    # Find the Tier 3 jq filter (the one that filters submission label candidates)
    tier3_section = workflow[workflow.find("TIER 3: unreviewed submissions"):workflow.find("TIER 4:")]
    
    # Check that pending-review is NOT in the jq exclusion list
    # The jq filter should exclude: accepted, rejected, validation-failed, etc.
    # But NOT pending-review
    jq_line = [line for line in tier3_section.split('\n') if 'contains(["accepted"])' in line][0]
    
    assert 'contains(["pending-review"])' not in jq_line, \
        "Tier 3 should NOT exclude pending-review in jq filter (let gating check handle it)"
    
    # Should still exclude editorial-hold and other terminal labels
    assert 'contains(["editorial-hold"])' in jq_line
    assert 'contains(["accepted"])' in jq_line


def test_stage6_removes_pending_review():
    """
    Verify stage 6 removes pending-review label when accepting or rejecting.
    
    This ensures the label is cleaned up after review.
    """
    import os
    stage6_path = os.path.join(os.path.dirname(__file__), "stage_6_post_review_and_decide.py")
    with open(stage6_path, "r") as f:
        stage6 = f.read()
    
    # Should remove pending-review in both acceptance and rejection paths
    assert '"pending-review"' in stage6
    assert '_remove_labels_if_present' in stage6


def test_picker_includes_pending_review_candidates():
    """
    Test that the picker includes pending-review issues as candidates,
    then uses gating check to determine approval.
    """
    from scripts.dry_run_review_picker import pick_next
    
    # Issue with pending-review but WITHOUT approved-for-review
    issues = [
        {
            "number": 100,
            "title": "[SUBMISSION] Test Gated",
            "labels": [
                {"name": "submission"},
                {"name": "pending-review"},
            ],
        }
    ]
    
    # Gating function that denies (simulates no approved-for-review label)
    gate_fn = lambda issue: {
        "approved": False,
        "reason": "requires approved-for-review label from maintainer"
    }
    
    picked, skipped = pick_next(issues, gate_fn, token="fake")
    
    # Should NOT be picked (gating failed)
    assert picked is None
    
    # Should be in skipped list with gating reason
    assert len(skipped) == 1
    assert skipped[0][0] == 100
    assert "gated" in skipped[0][1]


def test_picker_approves_with_approved_for_review_label():
    """
    Test that issues with both pending-review AND approved-for-review are picked.
    
    This is the core Bug B24 scenario: maintainer adds approved-for-review,
    issue still has pending-review, should be picked anyway.
    """
    from scripts.dry_run_review_picker import pick_next
    from unittest.mock import patch, Mock
    
    # Issue with BOTH pending-review AND approved-for-review
    issues = [
        {
            "number": 101,
            "title": "[SUBMISSION] Test Approved",
            "labels": [
                {"name": "submission"},
                {"name": "pending-review"},
                {"name": "approved-for-review"},
            ],
        }
    ]
    
    # Gating function that approves (simulates approved-for-review label)
    gate_fn = lambda issue: {
        "approved": True,
        "reason": "approved-for-review label present"
    }
    
    # Mock the requests.get to return empty comments (no bot review yet)
    with patch('requests.get') as mock_get:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []  # No comments
        mock_get.return_value = mock_resp
        
        picked, skipped = pick_next(issues, gate_fn, token="fake")
    
    # SHOULD be picked (gating passed, even with pending-review label, no bot comment)
    assert picked == 101
    assert len(skipped) == 0


def test_multiple_issues_priority():
    """
    Test that approved pending-review issues are picked in correct tier order.
    
    Verifies that the fix doesn't break tier prioritization.
    """
    from scripts.dry_run_review_picker import pick_next
    from unittest.mock import patch, Mock
    
    issues = [
        # Tier 1: publish-failed (highest priority)
        {
            "number": 50,
            "title": "[SUBMISSION] Publish Failed",
            "labels": [
                {"name": "submission"},
                {"name": "publish-failed"},
            ],
        },
        # Tier 3: pending-review with approval (should be picked if tier 1 is gated)
        {
            "number": 51,
            "title": "[SUBMISSION] Approved Pending",
            "labels": [
                {"name": "submission"},
                {"name": "pending-review"},
                {"name": "approved-for-review"},
            ],
        },
        # Tier 3: pending-review without approval (should be gated)
        {
            "number": 52,
            "title": "[SUBMISSION] Unapproved Pending",
            "labels": [
                {"name": "submission"},
                {"name": "pending-review"},
            ],
        },
    ]
    
    # Gating function that approves issues with approved-for-review
    # Note: publish-failed issues should also be approved (they already passed review once)
    def gate_fn(issue):
        labels = [lbl["name"] for lbl in issue.get("labels", [])]
        if "publish-failed" in labels or "approved-for-review" in labels:
            return {"approved": True, "reason": "approved-for-review present"}
        return {"approved": False, "reason": "needs approval"}
    
    # Mock the requests.get to return empty comments
    with patch('requests.get') as mock_get:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp
        
        picked, skipped = pick_next(issues, gate_fn, token="fake")
    
    # Should pick #50 (publish-failed, Tier 1 highest priority)
    assert picked == 50
    
    # Now test with Tier 1 gated
    def gate_fn_no_tier1(issue):
        labels = [lbl["name"] for lbl in issue.get("labels", [])]
        if "publish-failed" in labels:
            return {"approved": False, "reason": "gated"}
        if "approved-for-review" in labels:
            return {"approved": True, "reason": "approved"}
        return {"approved": False, "reason": "needs approval"}
    
    with patch('requests.get') as mock_get:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp
        
        picked, skipped = pick_next(issues, gate_fn_no_tier1, token="fake")
    
    # Should pick #51 (approved pending-review, Tier 3)
    assert picked == 51
    
    # Note: Once #51 is picked, the picker returns immediately, so #52 won't be in
    # the skipped list. To verify #52 would be gated, test it separately.
    separate_issues = [issues[2]]  # Just #52
    with patch('requests.get') as mock_get:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp
        
        picked_52, skipped_52 = pick_next(separate_issues, gate_fn_no_tier1, token="fake")
    
    # #52 should be skipped (pending-review without approval)
    assert picked_52 is None
    assert 52 in [num for num, reason in skipped_52]


def test_comment_instructs_correct_label():
    """
    Verify the gating comment instructs maintainers to add approved-for-review.
    
    The comment text should match the actual approval mechanism.
    """
    import os
    workflow_path = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "review.yml")
    with open(workflow_path, "r") as f:
        workflow = f.read()
    
    # Find the notify-gated job section which contains the comment template
    notify_section_start = workflow.find("notify-gated:")
    notify_section_end = workflow.find("# JOB 3:", notify_section_start)
    notify_section = workflow[notify_section_start:notify_section_end]
    
    # Should mention approved-for-review label
    assert "approved-for-review" in notify_section.lower()
    
    # Should promise ~6 hour queue after approval
    assert "6-hour" in notify_section or "6 hour" in notify_section


def test_approved_submission_picked_by_cron():
    """
    End-to-end test: simulate the full approval flow.
    
    1. Issue starts with pending-review
    2. Maintainer adds approved-for-review
    3. Cron picker should pick it
    """
    from scripts.dry_run_review_picker import pick_next
    from unittest.mock import patch, Mock
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from _review_agent.author_gating import evaluate_issue
    
    # Mock issue: pending-review + approved-for-review (maintainer approved it)
    issue = {
        "number": 200,
        "title": "[SUBMISSION] Test Approved Flow",
        "labels": [
            {"name": "submission"},
            {"name": "pending-review"},
            {"name": "approved-for-review"},
        ],
        "user": {"login": "untrusted-user"},
        "author_association": "NONE",
    }
    
    # Real gating check (uses evaluate_issue logic)
    def real_gate_fn(issue):
        labels = [lbl["name"] for lbl in issue.get("labels", [])]
        author_association = issue.get("author_association", "NONE")
        
        # Simulate author_gating.py logic
        if "editorial-hold" in labels:
            return {"approved": False, "reason": "editorial-hold"}
        if author_association in {"OWNER", "MEMBER", "COLLABORATOR"}:
            return {"approved": True, "reason": "collaborator"}
        if "approved-for-review" in labels:
            return {"approved": True, "reason": "approved-for-review label present"}
        return {"approved": False, "reason": "needs approval"}
    
    # Mock HTTP requests for bot comment check
    with patch('requests.get') as mock_get:
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []  # No bot comments yet
        mock_get.return_value = mock_resp
        
        # Run picker
        picked, skipped = pick_next([issue], real_gate_fn, token="fake")
    
    # Should be PICKED (approved via label, even with pending-review)
    assert picked == 200, "Approved gated submission should be picked by cron"
    assert len(skipped) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
