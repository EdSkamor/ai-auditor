"""
Portal PBC (Prepared by Client) + Zarządzanie Zleceniem
System zarządzania zleceniami audytowymi z checklistami PBC.
"""

import hashlib
import json
import logging
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import AuditorException, FileProcessingError, ValidationError


class AssignmentType(Enum):
    """Typy zleceń audytowych."""

    AUDIT = "audit"
    REVIEW = "review"
    AGREED_UPON = "agreed_upon"
    COMPLIANCE = "compliance"


class AssignmentStatus(Enum):
    """Statusy zlecenia."""

    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Statusy zadań."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class PBCItem:
    """Element checklisty PBC."""

    id: str
    title: str
    description: str
    category: str
    required: bool = True
    deadline: Optional[datetime] = None
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    comments: List[str] = None
    attachments: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.comments is None:
            self.comments = []
        if self.attachments is None:
            self.attachments = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class Assignment:
    """Zlecenie audytowe."""

    id: str
    title: str
    client_name: str
    assignment_type: AssignmentType
    status: AssignmentStatus
    start_date: datetime
    end_date: datetime
    assigned_auditor: str
    senior_auditor: Optional[str] = None
    partner: Optional[str] = None
    pbc_items: List[PBCItem] = None
    timeline: List[Dict[str, Any]] = None
    sla_requirements: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.pbc_items is None:
            self.pbc_items = []
        if self.timeline is None:
            self.timeline = []
        if self.sla_requirements is None:
            self.sla_requirements = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class WorkingPaper:
    """Working Paper - dokument roboczy."""

    id: str
    assignment_id: str
    title: str
    content: str
    file_path: Optional[str] = None
    hash_value: Optional[str] = None
    created_by: str = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_by is None:
            self.created_by = "system"
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.hash_value is None and self.content:
            self.hash_value = hashlib.sha256(self.content.encode()).hexdigest()


class PBCPortal:
    """Portal PBC + Zarządzanie Zleceniem."""

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / ".ai-auditor" / "pbc_portal"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Load data
        self.assignments: Dict[str, Assignment] = {}
        self.working_papers: Dict[str, WorkingPaper] = {}
        self._load_data()

        # Initialize default PBC templates
        self._initialize_pbc_templates()

    def _load_data(self):
        """Load assignments and working papers from disk."""
        try:
            # Load assignments
            assignments_file = self.data_dir / "assignments.json"
            if assignments_file.exists():
                with open(assignments_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for assignment_data in data:
                        assignment = self._dict_to_assignment(assignment_data)
                        self.assignments[assignment.id] = assignment

            # Load working papers
            wp_file = self.data_dir / "working_papers.json"
            if wp_file.exists():
                with open(wp_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for wp_data in data:
                        wp = self._dict_to_working_paper(wp_data)
                        self.working_papers[wp.id] = wp

            self.logger.info(
                f"Loaded {len(self.assignments)} assignments and {len(self.working_papers)} working papers"
            )

        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")

    def _save_data(self):
        """Save assignments and working papers to disk."""
        try:
            # Save assignments
            assignments_file = self.data_dir / "assignments.json"
            assignments_data = [
                asdict(assignment) for assignment in self.assignments.values()
            ]
            with open(assignments_file, "w", encoding="utf-8") as f:
                json.dump(assignments_data, f, indent=2, default=str)

            # Save working papers
            wp_file = self.data_dir / "working_papers.json"
            wp_data = [asdict(wp) for wp in self.working_papers.values()]
            with open(wp_file, "w", encoding="utf-8") as f:
                json.dump(wp_data, f, indent=2, default=str)

            self.logger.info("Data saved successfully")

        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise FileProcessingError(f"Failed to save data: {e}")

    def _dict_to_assignment(self, data: Dict[str, Any]) -> Assignment:
        """Convert dictionary to Assignment object."""
        # Convert PBC items
        pbc_items = []
        for item_data in data.get("pbc_items", []):
            pbc_item = PBCItem(**item_data)
            pbc_items.append(pbc_item)

        # Convert enums
        assignment_type = AssignmentType(data["assignment_type"])
        status = AssignmentStatus(data["status"])

        # Convert dates
        start_date = (
            datetime.fromisoformat(data["start_date"])
            if isinstance(data["start_date"], str)
            else data["start_date"]
        )
        end_date = (
            datetime.fromisoformat(data["end_date"])
            if isinstance(data["end_date"], str)
            else data["end_date"]
        )
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data["created_at"], str)
            else data["created_at"]
        )
        updated_at = (
            datetime.fromisoformat(data["updated_at"])
            if isinstance(data["updated_at"], str)
            else data["updated_at"]
        )

        return Assignment(
            id=data["id"],
            title=data["title"],
            client_name=data["client_name"],
            assignment_type=assignment_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            assigned_auditor=data["assigned_auditor"],
            senior_auditor=data.get("senior_auditor"),
            partner=data.get("partner"),
            pbc_items=pbc_items,
            timeline=data.get("timeline", []),
            sla_requirements=data.get("sla_requirements", {}),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _dict_to_working_paper(self, data: Dict[str, Any]) -> WorkingPaper:
        """Convert dictionary to WorkingPaper object."""
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data["created_at"], str)
            else data["created_at"]
        )
        updated_at = (
            datetime.fromisoformat(data["updated_at"])
            if isinstance(data["updated_at"], str)
            else data["updated_at"]
        )

        return WorkingPaper(
            id=data["id"],
            assignment_id=data["assignment_id"],
            title=data["title"],
            content=data["content"],
            file_path=data.get("file_path"),
            hash_value=data.get("hash_value"),
            created_by=data.get("created_by", "system"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _initialize_pbc_templates(self):
        """Initialize default PBC templates for different assignment types."""
        self.pbc_templates = {
            AssignmentType.AUDIT: [
                PBCItem(
                    id="audit_001",
                    title="Sprawozdania finansowe",
                    description="Bilans, rachunek zysków i strat, rachunek przepływów pieniężnych",
                    category="Financial Statements",
                    required=True,
                ),
                PBCItem(
                    id="audit_002",
                    title="Księgi rachunkowe",
                    description="Księga główna, księgi pomocnicze, dowody księgowe",
                    category="Accounting Records",
                    required=True,
                ),
                PBCItem(
                    id="audit_003",
                    title="Dokumentacja kontroli wewnętrznej",
                    description="Procedury, polityki, testy kontroli",
                    category="Internal Control",
                    required=True,
                ),
                PBCItem(
                    id="audit_004",
                    title="Umowy i zobowiązania",
                    description="Umowy długoterminowe, zobowiązania, gwarancje",
                    category="Contracts",
                    required=True,
                ),
                PBCItem(
                    id="audit_005",
                    title="Dokumentacja podatkowa",
                    description="JPK, deklaracje VAT, PIT, CIT",
                    category="Tax Documentation",
                    required=True,
                ),
            ],
            AssignmentType.REVIEW: [
                PBCItem(
                    id="review_001",
                    title="Sprawozdania finansowe",
                    description="Bilans, rachunek zysków i strat",
                    category="Financial Statements",
                    required=True,
                ),
                PBCItem(
                    id="review_002",
                    title="Księgi rachunkowe",
                    description="Księga główna, dowody księgowe",
                    category="Accounting Records",
                    required=True,
                ),
            ],
            AssignmentType.AGREED_UPON: [
                PBCItem(
                    id="agreed_001",
                    title="Dokumentacja zgodności",
                    description="Dokumenty potwierdzające zgodność z umową",
                    category="Compliance",
                    required=True,
                )
            ],
        }

    def create_assignment(
        self,
        title: str,
        client_name: str,
        assignment_type: AssignmentType,
        start_date: datetime,
        end_date: datetime,
        assigned_auditor: str,
        senior_auditor: str = None,
        partner: str = None,
    ) -> Assignment:
        """Create new assignment."""
        try:
            # Generate unique ID with microseconds
            now = datetime.now()
            assignment_id = f"ASS_{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond}"

            # Create assignment
            assignment = Assignment(
                id=assignment_id,
                title=title,
                client_name=client_name,
                assignment_type=assignment_type,
                status=AssignmentStatus.DRAFT,
                start_date=start_date,
                end_date=end_date,
                assigned_auditor=assigned_auditor,
                senior_auditor=senior_auditor,
                partner=partner,
            )

            # Add PBC items from template
            if assignment_type in self.pbc_templates:
                assignment.pbc_items = [
                    PBCItem(**asdict(item))
                    for item in self.pbc_templates[assignment_type]
                ]

            # Add to assignments
            self.assignments[assignment_id] = assignment

            # Save data
            self._save_data()

            self.logger.info(f"Created assignment: {assignment_id}")
            return assignment

        except Exception as e:
            self.logger.error(f"Failed to create assignment: {e}")
            raise AuditorException(f"Failed to create assignment: {e}")

    def get_assignment(self, assignment_id: str) -> Optional[Assignment]:
        """Get assignment by ID."""
        return self.assignments.get(assignment_id)

    def list_assignments(
        self, status: AssignmentStatus = None, auditor: str = None, client: str = None
    ) -> List[Assignment]:
        """List assignments with optional filters."""
        assignments = list(self.assignments.values())

        if status:
            assignments = [a for a in assignments if a.status == status]

        if auditor:
            assignments = [a for a in assignments if a.assigned_auditor == auditor]

        if client:
            assignments = [
                a for a in assignments if client.lower() in a.client_name.lower()
            ]

        return sorted(assignments, key=lambda x: x.created_at, reverse=True)

    def update_assignment_status(
        self, assignment_id: str, status: AssignmentStatus
    ) -> bool:
        """Update assignment status."""
        assignment = self.assignments.get(assignment_id)
        if not assignment:
            return False

        assignment.status = status
        assignment.updated_at = datetime.now()

        self._save_data()
        self.logger.info(f"Updated assignment {assignment_id} status to {status.value}")
        return True

    def update_pbc_item_status(
        self, assignment_id: str, item_id: str, status: TaskStatus, comment: str = None
    ) -> bool:
        """Update PBC item status."""
        assignment = self.assignments.get(assignment_id)
        if not assignment:
            return False

        for item in assignment.pbc_items:
            if item.id == item_id:
                item.status = status
                item.updated_at = datetime.now()
                if comment:
                    item.comments.append(
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {comment}"
                    )

                self._save_data()
                self.logger.info(f"Updated PBC item {item_id} status to {status.value}")
                return True

        return False

    def add_working_paper(
        self,
        assignment_id: str,
        title: str,
        content: str,
        file_path: str = None,
        created_by: str = None,
    ) -> WorkingPaper:
        """Add working paper to assignment."""
        try:
            # Generate unique ID with microseconds
            now = datetime.now()
            wp_id = f"WP_{now.strftime('%Y%m%d_%H%M%S')}_{now.microsecond}"

            wp = WorkingPaper(
                id=wp_id,
                assignment_id=assignment_id,
                title=title,
                content=content,
                file_path=file_path,
                created_by=created_by or "system",
            )

            self.working_papers[wp_id] = wp
            self._save_data()

            self.logger.info(f"Added working paper: {wp_id}")
            return wp

        except Exception as e:
            self.logger.error(f"Failed to add working paper: {e}")
            raise AuditorException(f"Failed to add working paper: {e}")

    def export_working_papers(
        self, assignment_id: str, output_dir: Path = None
    ) -> Path:
        """Export working papers for assignment as ZIP."""
        try:
            if output_dir is None:
                output_dir = self.data_dir / "exports"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get working papers for assignment
            wps = [
                wp
                for wp in self.working_papers.values()
                if wp.assignment_id == assignment_id
            ]

            if not wps:
                raise ValidationError(
                    f"No working papers found for assignment {assignment_id}"
                )

            # Create ZIP file
            zip_path = (
                output_dir
                / f"working_papers_{assignment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add working papers
                for wp in wps:
                    # Add content as text file
                    content_file = f"{wp.id}_{wp.title.replace(' ', '_')}.txt"
                    zipf.writestr(content_file, wp.content)

                    # Add metadata
                    metadata = {
                        "id": wp.id,
                        "title": wp.title,
                        "created_by": wp.created_by,
                        "created_at": wp.created_at.isoformat(),
                        "hash_value": wp.hash_value,
                    }
                    metadata_file = f"{wp.id}_metadata.json"
                    zipf.writestr(metadata_file, json.dumps(metadata, indent=2))

                # Add manifest
                manifest = {
                    "assignment_id": assignment_id,
                    "export_date": datetime.now().isoformat(),
                    "working_papers_count": len(wps),
                    "files": [
                        f"{wp.id}_{wp.title.replace(' ', '_')}.txt" for wp in wps
                    ],
                }
                zipf.writestr("MANIFEST.json", json.dumps(manifest, indent=2))

            self.logger.info(f"Exported {len(wps)} working papers to {zip_path}")
            return zip_path

        except Exception as e:
            self.logger.error(f"Failed to export working papers: {e}")
            raise FileProcessingError(f"Failed to export working papers: {e}")

    def get_assignment_timeline(self, assignment_id: str) -> List[Dict[str, Any]]:
        """Get assignment timeline with SLA tracking."""
        assignment = self.assignments.get(assignment_id)
        if not assignment:
            return []

        timeline = []

        # Add assignment milestones
        timeline.append(
            {
                "date": assignment.start_date,
                "event": "Assignment Started",
                "status": (
                    "completed"
                    if assignment.status != AssignmentStatus.DRAFT
                    else "pending"
                ),
                "description": f"Assignment {assignment.title} started",
            }
        )

        # Add PBC item deadlines
        for item in assignment.pbc_items:
            if item.deadline:
                timeline.append(
                    {
                        "date": item.deadline,
                        "event": f"PBC Deadline: {item.title}",
                        "status": (
                            "completed"
                            if item.status == TaskStatus.COMPLETED
                            else "pending"
                        ),
                        "description": f"Deadline for {item.title}",
                    }
                )

        # Add assignment end
        timeline.append(
            {
                "date": assignment.end_date,
                "event": "Assignment Due",
                "status": (
                    "completed"
                    if assignment.status == AssignmentStatus.COMPLETED
                    else "pending"
                ),
                "description": f"Assignment {assignment.title} due",
            }
        )

        return sorted(timeline, key=lambda x: x["date"])

    def get_assignment_statistics(self, assignment_id: str) -> Dict[str, Any]:
        """Get assignment statistics."""
        assignment = self.assignments.get(assignment_id)
        if not assignment:
            return {}

        total_items = len(assignment.pbc_items)
        completed_items = len(
            [
                item
                for item in assignment.pbc_items
                if item.status == TaskStatus.COMPLETED
            ]
        )
        pending_items = len(
            [item for item in assignment.pbc_items if item.status == TaskStatus.PENDING]
        )
        in_progress_items = len(
            [
                item
                for item in assignment.pbc_items
                if item.status == TaskStatus.IN_PROGRESS
            ]
        )

        # Calculate progress
        progress = (completed_items / total_items * 100) if total_items > 0 else 0

        # Calculate days remaining
        days_remaining = (assignment.end_date - datetime.now()).days

        return {
            "assignment_id": assignment_id,
            "title": assignment.title,
            "client_name": assignment.client_name,
            "status": assignment.status.value,
            "progress_percentage": round(progress, 2),
            "total_pbc_items": total_items,
            "completed_items": completed_items,
            "pending_items": pending_items,
            "in_progress_items": in_progress_items,
            "days_remaining": days_remaining,
            "working_papers_count": len(
                [
                    wp
                    for wp in self.working_papers.values()
                    if wp.assignment_id == assignment_id
                ]
            ),
        }
