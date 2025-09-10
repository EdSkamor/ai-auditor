#!/usr/bin/env python3
"""
Test script for PBC Portal functionality.
"""

import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.pbc_portal import AssignmentStatus, AssignmentType, PBCPortal, TaskStatus


def test_pbc_portal():
    """Test PBC Portal functionality."""
    print("🚀 Starting PBC Portal Test Suite...")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Initialize portal
        print("🧪 Testing PBC Portal Initialization...")
        portal = PBCPortal(tmp_path)
        print("✅ PBC Portal initialized successfully")

        # Test assignment creation
        print("\n🧪 Testing Assignment Creation...")
        assignment = portal.create_assignment(
            title="Audyt roczny 2024",
            client_name="ACME Corporation Sp. z o.o.",
            assignment_type=AssignmentType.AUDIT,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            assigned_auditor="Jan Kowalski",
            senior_auditor="Anna Nowak",
            partner="Piotr Wiśniewski",
        )

        print(f"✅ Assignment created: {assignment.id}")
        print(f"   Title: {assignment.title}")
        print(f"   Client: {assignment.client_name}")
        print(f"   Type: {assignment.assignment_type.value}")
        print(f"   PBC Items: {len(assignment.pbc_items)}")

        # Test PBC items
        print("\n🧪 Testing PBC Items...")
        for item in assignment.pbc_items[:3]:  # Show first 3 items
            print(f"   • {item.title} ({item.category}) - Required: {item.required}")

        # Test assignment retrieval
        print("\n🧪 Testing Assignment Retrieval...")
        retrieved_assignment = portal.get_assignment(assignment.id)
        assert retrieved_assignment is not None
        assert retrieved_assignment.title == assignment.title
        print("✅ Assignment retrieved successfully")

        # Test assignment listing
        print("\n🧪 Testing Assignment Listing...")
        assignments = portal.list_assignments()
        assert len(assignments) == 1
        print(f"✅ Found {len(assignments)} assignments")

        # Test status update
        print("\n🧪 Testing Status Updates...")
        portal.update_assignment_status(assignment.id, AssignmentStatus.ACTIVE)
        updated_assignment = portal.get_assignment(assignment.id)
        assert updated_assignment.status == AssignmentStatus.ACTIVE
        print("✅ Assignment status updated successfully")

        # Test PBC item status update
        print("\n🧪 Testing PBC Item Status Update...")
        pbc_item = assignment.pbc_items[0]
        portal.update_pbc_item_status(
            assignment.id,
            pbc_item.id,
            TaskStatus.COMPLETED,
            "Dokumenty dostarczone przez klienta",
        )
        updated_assignment = portal.get_assignment(assignment.id)
        updated_item = next(
            item for item in updated_assignment.pbc_items if item.id == pbc_item.id
        )
        assert updated_item.status == TaskStatus.COMPLETED
        assert len(updated_item.comments) > 0
        print("✅ PBC item status updated successfully")

        # Test working paper creation
        print("\n🧪 Testing Working Paper Creation...")
        wp = portal.add_working_paper(
            assignment_id=assignment.id,
            title="Test kontroli wewnętrznej",
            content="Wyniki testów kontroli wewnętrznej dla procesu sprzedaży...",
            created_by="Jan Kowalski",
        )
        print(f"✅ Working paper created: {wp.id}")
        print(f"   Title: {wp.title}")
        print(f"   Hash: {wp.hash_value[:16]}...")

        # Test working paper export
        print("\n🧪 Testing Working Paper Export...")
        export_path = portal.export_working_papers(assignment.id)
        assert export_path.exists()
        print(f"✅ Working papers exported to: {export_path.name}")

        # Test assignment statistics
        print("\n🧪 Testing Assignment Statistics...")
        stats = portal.get_assignment_statistics(assignment.id)
        assert stats["assignment_id"] == assignment.id
        assert stats["total_pbc_items"] > 0
        assert stats["progress_percentage"] >= 0
        print("✅ Assignment statistics:")
        print(f"   Progress: {stats['progress_percentage']}%")
        print(
            f"   Completed items: {stats['completed_items']}/{stats['total_pbc_items']}"
        )
        print(f"   Days remaining: {stats['days_remaining']}")

        # Test timeline
        print("\n🧪 Testing Assignment Timeline...")
        timeline = portal.get_assignment_timeline(assignment.id)
        assert len(timeline) > 0
        print(f"✅ Timeline created with {len(timeline)} events")
        for event in timeline[:2]:  # Show first 2 events
            print(f"   • {event['date'].strftime('%Y-%m-%d')}: {event['event']}")

        # Test multiple assignments
        print("\n🧪 Testing Multiple Assignments...")
        assignment2 = portal.create_assignment(
            title="Przegląd kwartalny Q1",
            client_name="Test Company Ltd.",
            assignment_type=AssignmentType.REVIEW,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=14),
            assigned_auditor="Maria Kowalczyk",
        )

        all_assignments = portal.list_assignments()
        assert len(all_assignments) == 2
        print(f"✅ Created second assignment: {assignment2.id}")

        # Test filtering
        audit_assignments = portal.list_assignments(status=AssignmentStatus.ACTIVE)
        assert len(audit_assignments) == 1
        print(f"✅ Filtered assignments: {len(audit_assignments)} active assignments")

        print("\n" + "=" * 60)
        print("📊 PBC Portal Test Results: All tests passed!")
        print("🎉 PBC Portal is working correctly!")


if __name__ == "__main__":
    test_pbc_portal()
