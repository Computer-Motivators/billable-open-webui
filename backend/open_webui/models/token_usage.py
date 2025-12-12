import time
from typing import Optional
from datetime import datetime, timedelta

from open_webui.internal.db import Base, get_db
from open_webui.env import SRC_LOG_LEVELS

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    BigInteger,
    Column,
    String,
    Text,
    Integer,
    Index,
)

import logging

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# TokenUsage DB Schema
####################


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(Text, unique=True, primary_key=True)
    user_id = Column(Text, nullable=False, index=True)
    
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    
    created_at = Column(BigInteger, nullable=False, index=True)

    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )


class TokenUsageModel(BaseModel):
    id: str
    user_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    created_at: int  # timestamp in epoch

    model_config = ConfigDict(from_attributes=True)


class TokenUsageSummary(BaseModel):
    user_id: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    period_days: int


####################
# TokenUsage Table
####################


class TokenUsageTable:
    def insert_token_usage(
        self,
        user_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> Optional[TokenUsageModel]:
        try:
            import uuid
            total_tokens = input_tokens + output_tokens
            now = int(time.time())
            
            with get_db() as db:
                token_usage = TokenUsage(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    created_at=now,
                )
                db.add(token_usage)
                db.commit()
                db.refresh(token_usage)
                return TokenUsageModel.model_validate(token_usage)
        except Exception as e:
            log.exception(f"Error inserting token usage: {e}")
            return None

    def get_user_token_usage(
        self,
        user_id: str,
        days: int = 30,
    ) -> TokenUsageSummary:
        """
        Get token usage summary for a user over the last N days.
        """
        try:
            with get_db() as db:
                cutoff_time = int(time.time()) - (days * 24 * 60 * 60)
                
                from sqlalchemy import func
                result = (
                    db.query(
                        func.sum(TokenUsage.input_tokens).label('total_input'),
                        func.sum(TokenUsage.output_tokens).label('total_output'),
                        func.sum(TokenUsage.total_tokens).label('total'),
                    )
                    .filter(
                        TokenUsage.user_id == user_id,
                        TokenUsage.created_at >= cutoff_time,
                    )
                    .first()
                )
                
                return TokenUsageSummary(
                    user_id=user_id,
                    total_input_tokens=int(result.total_input or 0),
                    total_output_tokens=int(result.total_output or 0),
                    total_tokens=int(result.total or 0),
                    period_days=days,
                )
        except Exception as e:
            log.exception(f"Error getting token usage: {e}")
            return TokenUsageSummary(
                user_id=user_id,
                total_input_tokens=0,
                total_output_tokens=0,
                total_tokens=0,
                period_days=days,
            )

    def get_all_users_token_usage(
        self,
        days: int = 30,
    ) -> dict[str, TokenUsageSummary]:
        """
        Get token usage summary for all users over the last N days.
        Returns a dictionary mapping user_id to TokenUsageSummary.
        """
        try:
            with get_db() as db:
                cutoff_time = int(time.time()) - (days * 24 * 60 * 60)
                
                from sqlalchemy import func
                results = (
                    db.query(
                        TokenUsage.user_id,
                        func.sum(TokenUsage.input_tokens).label('total_input'),
                        func.sum(TokenUsage.output_tokens).label('total_output'),
                        func.sum(TokenUsage.total_tokens).label('total'),
                    )
                    .filter(TokenUsage.created_at >= cutoff_time)
                    .group_by(TokenUsage.user_id)
                    .all()
                )
                
                usage_dict = {}
                for user_id, total_input, total_output, total in results:
                    usage_dict[user_id] = TokenUsageSummary(
                        user_id=user_id,
                        total_input_tokens=int(total_input or 0),
                        total_output_tokens=int(total_output or 0),
                        total_tokens=int(total or 0),
                        period_days=days,
                    )
                
                return usage_dict
        except Exception as e:
            log.exception(f"Error getting all users token usage: {e}")
            return {}

    def cleanup_old_records(self, days: int = 30) -> int:
        """
        Delete token usage records older than N days.
        Returns the number of deleted records.
        """
        try:
            with get_db() as db:
                cutoff_time = int(time.time()) - (days * 24 * 60 * 60)
                deleted = (
                    db.query(TokenUsage)
                    .filter(TokenUsage.created_at < cutoff_time)
                    .delete()
                )
                db.commit()
                return deleted
        except Exception as e:
            log.exception(f"Error cleaning up old token usage records: {e}")
            return 0


TokenUsages = TokenUsageTable()

