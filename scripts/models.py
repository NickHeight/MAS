"""Pydantic schemas for MAS inter-agent handoffs."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ClientModule(str, Enum):
    WEB = "web"
    AUTOMATION = "automation"
    AI_AGENTS = "ai_agents"


class GlobalState(BaseModel):
    """Stub for future LangGraph integration. TASKS.md is live state for now."""

    trigger_source: str = "cursor"
    domains: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    shared_context: dict[str, Any] = Field(default_factory=dict)
    active_blueprints: dict[str, Any] = Field(default_factory=dict)
    execution_status: str = "pending"
    error_logs: list[str] = Field(default_factory=list)


class ClientScaffoldRequest(BaseModel):
    name: str
    slug: str
    modules: list[ClientModule]
    description: str = ""

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        import re

        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", v):
            raise ValueError("slug must be lowercase alphanumeric with hyphens only")
        return v


class ClientScaffoldResult(BaseModel):
    project_path: str
    wiki_path: str
    entity_path: str
    modules: list[str]
    monday_checklist: list[str]
    dry_run: bool = False


class ProposedMove(BaseModel):
    source: str
    destination: str
    module: str
    reason: str


class MigrationPlan(BaseModel):
    source_path: str
    analyzed_at: str
    proposed_moves: list[ProposedMove]
    risks: list[str]
    unmapped_files: list[str]
    approval_required: bool = True
    analysis_method: str  # "heuristic" | "gemini"


class MondayChecklist(BaseModel):
    """Stub until Monday.com API worker is implemented."""

    client_name: str
    slug: str
    steps: list[str] = Field(
        default_factory=lambda: [
            "Create Monday workspace per monday-board-template.md",
            "Create internal board: {name} Automation — Internal Build",
            "Create client board: {name} — Development Portal",
            "Add 'How to use this workspace with your AI' Doc",
            "Configure automations per template",
            "Post welcome item to client board",
            "Record board IDs in wiki 00_overview.md Monday IDs section",
        ]
    )

    def render(self) -> list[str]:
        return [step.format(name=self.client_name) for step in self.steps]


class ZoneClass(str, Enum):
    CLIENT_BUNDLE = "client_bundle"
    REFERENCE_ONLY = "reference_only"
    INTERNAL_PIPELINE = "internal_pipeline"
    PORTFOLIO = "portfolio"
    WIKI_REPO = "wiki_repo"
    ARCHIVE = "archive"
    AGENCY = "agency"
    MESSAGES = "messages"
    UNKNOWN = "unknown"


class GitRepoInfo(BaseModel):
    local_path: str
    remote_url: str | None = None
    immutable: bool = True


class ClientBundlePaths(BaseModel):
    reference: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    wiki: str | None = None
    global_kb_entity: str | None = None
    message_backups: str | None = None  # external path (OneDrive SMS Backup XML)


class MessageBackupZone(BaseModel):
    """External SMS Backup & Restore export location (outside ~/Upwork/)."""

    local_path: str
    format: str = "sms-backup-restore-xml"
    sync: str = "onedrive"
    file_count: int = 0
    contacts: dict[str, int] = Field(default_factory=dict)
    linked_slugs: list[str] = Field(default_factory=list)


class FourPillarStatus(BaseModel):
    project_filesystem: bool = False
    upwork_wiki: bool = False
    global_kb_entity: bool = False
    monday_workspace: bool = False
    claude_md_in_primary_project: bool = False


class ClientBundle(BaseModel):
    slug: str
    display_name: str
    paths: ClientBundlePaths
    git_repos: list[GitRepoInfo] = Field(default_factory=list)
    four_pillar_status: FourPillarStatus = Field(default_factory=FourPillarStatus)
    modules: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    sms_contacts: list[str] = Field(default_factory=list)  # contact_name in SMS backups


class SystemEntry(BaseModel):
    name: str
    zone_class: ZoneClass
    local_path: str
    purpose: str = ""
    git_repos: list[GitRepoInfo] = Field(default_factory=list)
    immutable: bool = True


class OrphanFile(BaseModel):
    source: str
    suggested_destination: str
    reason: str


class ReadmeTableRow(BaseModel):
    local_path: str
    purpose: str
    github_repo: str | None = None


class UpworkInventory(BaseModel):
    audited_at: str
    upwork_root: str
    readme_rows: list[ReadmeTableRow] = Field(default_factory=list)
    client_bundles: list[ClientBundle] = Field(default_factory=list)
    systems: list[SystemEntry] = Field(default_factory=list)
    reference_folders: list[str] = Field(default_factory=list)
    orphans: list[OrphanFile] = Field(default_factory=list)
    unmapped_wiki_clients: list[str] = Field(default_factory=list)
    message_backup_zone: MessageBackupZone | None = None
