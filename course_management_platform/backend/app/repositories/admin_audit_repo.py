from sqlalchemy.orm import Session

from app.models.admin_audit import AdminAudit


def log_admin_action(
    db: Session,
    admin_user_id: int = None,
    admin_level: str = None,
    action: str = None,
    method: str = None,
    status_code: int = None
):

    record = AdminAudit(
        admin_user_id=admin_user_id,
        admin_level=admin_level,
        action=action,
        method=method,
        status_code=status_code
    )

    db.add(record)
    db.commit()