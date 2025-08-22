from typing import List, Optional
from sqlmodel import Session, select

from models.estimation import Estimation


def create_estimation(
    session: Session,
    title: str,
    min_value: int,
    max_value: int
) -> Estimation:
    """Create a new estimation record"""
    estimation = Estimation(
        title=title,
        max_value=max_value,
        min_value=min_value
    )
    session.add(estimation)
    session.commit()
    session.refresh(estimation)
    return estimation


def get_estimation_by_id(session: Session, estimation_id: int) -> Optional[Estimation]:
    """Get an estimation by ID"""
    statement = select(Estimation).where(Estimation.id == estimation_id)
    return session.exec(statement).first()


def get_estimations(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Estimation]:
    """Get list of estimations with pagination"""
    statement = (
        select(Estimation)
        .offset(skip)
        .limit(limit)
        .order_by(Estimation.created_at.desc())
    )
    return list(session.exec(statement).all())


def update_estimation(
    session: Session,
    estimation_id: int,
    title: Optional[str] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> Optional[Estimation]:
    """Update an existing estimation"""
    estimation = get_estimation_by_id(session, estimation_id)
    if not estimation:
        return None
    
    if title is not None:
        estimation.title = title
    if min_value is not None:
        estimation.min_value = min_value
    if max_value is not None:
        estimation.max_value = max_value
    
    session.add(estimation)
    session.commit()
    session.refresh(estimation)
    return estimation


def delete_estimation(session: Session, estimation_id: int) -> bool:
    """Delete an estimation"""
    estimation = get_estimation_by_id(session, estimation_id)
    if not estimation:
        return False
    
    session.delete(estimation)
    session.commit()
    return True