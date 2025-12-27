# -*- coding: utf-8 -*-
"""
Orchestrators 模組 - 業務流程編排層

此模組提供業務流程的統一編排，將複雜的多步驟操作抽象為可重用的 Orchestrator。

主要類別:
    - BaseOrchestrator: 所有 Orchestrator 的抽象基類
    - IntelligentRecommendationOrchestrator: 智能推薦執行編排
    - HybridScanOrchestrator: 混合掃描編排
    - DurationSendOrchestrator: 時長發送編排

使用方式:
    from src.orchestrators import IntelligentRecommendationOrchestrator

    orchestrator = IntelligentRecommendationOrchestrator(config)
    result = orchestrator.execute(scheduler=scheduler)
"""

from .base_orchestrator import BaseOrchestrator, OrchestratorResult
from .intelligent_recommendation import IntelligentRecommendationOrchestrator
from .hybrid_scan import HybridScanOrchestrator, HybridMode
from .duration_send import DurationSendOrchestrator

__all__ = [
    'BaseOrchestrator',
    'OrchestratorResult',
    'IntelligentRecommendationOrchestrator',
    'HybridScanOrchestrator',
    'HybridMode',
    'DurationSendOrchestrator',
]
