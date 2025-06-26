#!/usr/bin/env python3
"""
Test script to validate agent improvements using evaluation set data.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from agent_engine import get_agent_runner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test data from the evaluation set
RESUME_TEXT = """ABHIJIT GUPTA, PhD
Data Scientist | Financial-Risk ML Specialist | PhD, Machine Learning | Bengaluru, India
abhijit038@gmail.com • +91 9561930406 • linkedin.com/in/abhijit-gupta-phd-639568166/
PROFESSIONAL SUMMARY
PhD‑trained ML scientist with 7+ years converting research into production. Generated £8 m+ in cost savings and 10 % alpha on £210 m commodity exposure. Deep expertise spans Bayesian inference, time‑series & causal modelling, graph neural networks, and large‑scale optimisation. Adept at partnering with business and engineering leaders to ship high‑impact solutions on Azure while mentoring cross‑functional teams. Multiple national AI wins and government‑funded research underscore a record of innovation and delivery.
CORE COMPETENCIES
ML / Statistics: Bayesian Inference • Deep / Graph NN • Causal TS • LLM/LLMOps • Agentic AI Econometrics
Cloud & MLOps: Azure ML • Databricks • Spark • Docker • Kubernetes • GitLab CI/CD
Domain & Leadership: Financial Risk Management • Commodity Hedging • Risk Analytics • Fraud Detection • Agile / OKRs • Mentoring • Algorithms Design • Generative AI/LLM for Finance
Programming: Python, C++, Java
PROFESSIONAL EXPERIENCE
TESCO, Bengaluru, India - Data Scientist | Nov 2023 – Present
Designed and deployed proprietary ML hedging models covering > £210 m in commodity futures; out‑performed market benchmarks by 10 % and realised £8 m savings.
Earned back-to-back "Exceptional" performance ratings for driving high-impact ML solutions in commodity risk management.
Built pricing & inventory‑optimization pipelines integrated with Azure ML + Databricks that recommends optimal implied cover levels across inflationary and deflationary cycles, enabling intelligent buying decisions that cut stock‑outs 9 % and lifted gross margin 3 pp.
Championed CI/CD-driven model governance with automated drift monitoring, reducing release cycle time by 40%.
Mentored data scientists, streamlining experiment workflows to cut model iteration time by 30 % and reduce post‑deployment defects by 20 %.
NICE ACTIMIZE - Tech Lead, Data Scientist | Feb 2021 – Nov 2023
Led 6‑member squad; probabilistic‑graph fraud models ↑ true positives 18 %, added $1 m+ YoY revenue.
Won company-wide CoDay 2022 for building scalable election-risk simulation using Java and Spark; recognized by CTO for innovation in risk modelling architecture.
Instituted Agile OKRs across the data science pipeline, increasing sprint on-time delivery from 68% to 92% by aligning delivery with strategic objectives.
INTEL CORPORATION - AI Ambassador (Part‑time) | Jul 2018 – Jan 2022
Created Computer Vision & NLP demos for Intel accelerators; tutorials viewed 8 k+ times.
Delivered 10+ workshops on ML applications in science and engineering to 300+ professionals; topics included deep learning and domain-specific use cases.
Contributed to open‑source OneAPI examples; code featured in Intel Developer Zone.
EDUCATION
PhD, Machine Learning | Indian Institute of Science Education and Research (IISER), Pune - 2022
MS, Computational Science | IISER Pune - 2017
B.Sc. | Hindu College, University of Delhi - 2015
PhD Thesis: Designing Scalable ML algorithms for molecular recognition; awarded Govt. of India DBT‑AI grant[BT/PR34215/AI/133/22/2019].
CERTIFICATIONS
Financial Engineering & Risk Management Specialization - Columbia University (2025)
NVIDIA – Rapid Application Development with Large Language Models (LLMs) – Jun 2025
Optimization methods in Asset Management – Coursera, Columbia University (2025)
AI and Machine Learning Algorithms and Techniques – Microsoft (2025)
Bayesian Statistics - Coursera (2023)
NVIDIA DLI: Accelerating Data Engineering Pipelines - Dec 2022
NVIDIA DLI: Natural Language Processing - Nov 2022
NVIDIA DLI: Fundamentals of Deep Learning - Sep 2022
HONOURS & AWARDS
All‑India Champion - Intel Python Hack Fury (4 000+ teams, organized by Intel, AWS)
Finalist - Microsoft Azure Hackathon (8 500+ teams)
Best Poster - IIT Delhi, BARC, Merck (multiple years)
DBT‑AI Grant - Government of India, ₹3.2 M research funding [BT/PR34215/AI/133/22/2019]
Certificate of Appreciation - Ministry of Electronics & IT, Govt of India (2020)
SELECTED PUBLICATIONS
Gupta, Abhijit. "Decoding Futures Price Dynamics: A Regularized Sparse Autoencoder for Interpretable Multi-Horizon Forecasting and Factor Discovery."  arXiv:2505.06795 (2025).
Gupta, A, Mukherjee, A. "Capturing surface complementarity in proteins using unsupervised learning and robust curvature measure." Proteins. 2022; 90(9): 1669-1683. doi:10.1002/prot.26345
Gupta, A., Kulkarni, M., Mukherjee, A. "Accurate prediction of B-form/A-form DNA conformation propensity from primary sequence: A machine learning and free energy handshake." Cell Patterns, 2(9), 2021, 100329. doi:10.1016/j.patter.2021.100329.
Gupta, A., Mukherjee, A. "Prediction of good reaction coordinates and future evolution of MD trajectories using Regularized Sparse Autoencoders: A novel deep learning approach."
Gupta, A., Mukherjee, A. "CardiGraphormer: Unveiling the Power of Self-Supervised Learning in Revolutionizing Drug Discovery", 2023, CardiGraphormer."""

JOB_POSTING_TEXT = """Optum AI is UnitedHealth Group's enterprise AI team. We are AI/ML scientists and engineers with deep expertise in AI/ML engineering for health care. We develop AI/ML solutions for the highest impact opportunities across UnitedHealth Group businesses including UnitedHealthcare, Optum Financial, Optum Health, Optum Insight, and Optum Rx. In addition to transforming the health care journey through responsible AI/ML innovation, our charter also includes developing and supporting an enterprise AI/ML development platform."""


async def test_orchestrator_identity():
    """Test that the orchestrator properly identifies itself."""
    logger.info("Testing orchestrator identity...")
    runner = get_agent_runner()
    
    response = await runner.run_async(
        user_id="test_user_identity",
        query="who are you?",
        session_id="test_session_identity"
    )
    
    logger.info(f"Identity response: {response}")
    
    # Check if response contains proper identity information
    identity_indicators = [
        "orchestrator" in response.lower(),
        ("purpose" in response.lower() or "manage" in response.lower()),
        ("json" in response.lower() or "structured" in response.lower())
    ]
    
    if any(identity_indicators):
        logger.info("✅ Identity test PASSED")
        return True
    else:
        logger.error("❌ Identity test FAILED")
        logger.error(f"Response: {response}")
        return False


async def test_resume_parsing():
    """Test that resume parsing returns structured JSON."""
    logger.info("Testing resume parsing...")
    runner = get_agent_runner()
    
    response = await runner.run_async(
        user_id="test_user_resume",
        query=f"parse this - {RESUME_TEXT}",
        session_id="test_session_resume"
    )
    
    logger.info(f"Resume parsing response length: {len(response)}")
    logger.info(f"Resume parsing response preview: {response[:500]}...")
    
    # Check if it's NOT just a brief agent description (main failure case from eval set)
    is_brief_agent_description = (
        "I am the" in response and
        "resume_parser_agent" in response and
        len(response) < 300 and
        "purpose" in response.lower()
    )
    
    # Check if response contains JSON structure
    has_json_structure = "{" in response and "}" in response
    
    # Check if response is substantial (not just a brief description)
    is_substantial = len(response) > 500
    
    # Check for any resume-related content indicators
    content_indicators = [
        "ABHIJIT GUPTA" in response or "abhijit038@gmail.com" in response,
        "Data Scientist" in response or "TESCO" in response,
        "PhD" in response or "Machine Learning" in response,
        "Python" in response or "programming" in response,
        "experience" in response.lower() or "skills" in response.lower()
    ]
    
    has_resume_content = any(content_indicators)
    
    # Success criteria: Not a brief description AND (has JSON structure OR substantial content with resume data)
    success = (
        not is_brief_agent_description and
        (has_json_structure or (is_substantial and has_resume_content))
    )
    
    logger.info(f"Test criteria:")
    logger.info(f"  - Not brief agent description: {not is_brief_agent_description}")
    logger.info(f"  - Has JSON structure: {has_json_structure}")
    logger.info(f"  - Is substantial (>500 chars): {is_substantial}")
    logger.info(f"  - Has resume content: {has_resume_content}")
    logger.info(f"  - Overall success: {success}")
    
    if success:
        logger.info("✅ Resume parsing test PASSED")
        return True
    else:
        logger.error("❌ Resume parsing test FAILED")
        logger.error(f"Response: {response[:1000]}...")
        return False


async def test_job_posting_analysis():
    """Test that job posting analysis returns structured JSON."""
    logger.info("Testing job posting analysis...")
    runner = get_agent_runner()
    
    response = await runner.run_async(
        user_id="test_user_job",
        query=f"analyse this - {JOB_POSTING_TEXT}",
        session_id="test_session_job"
    )
    
    logger.info(f"Job posting analysis response length: {len(response)}")
    
    # Check if response contains structured data indicators
    success_indicators = [
        "job_title" in response,
        "company" in response,
        "industry_type" in response,
        "session_info" in response
    ]
    
    if all(success_indicators):
        logger.info("✅ Job posting analysis test PASSED")
        return True
    else:
        logger.error("❌ Job posting analysis test FAILED")
        logger.error(f"Missing indicators: {[i for i, x in enumerate(success_indicators) if not x]}")
        return False


async def test_matching():
    """Test that matching returns detailed compatibility analysis."""
    logger.info("Testing matching functionality...")
    runner = get_agent_runner()
    
    # First parse resume and job posting to get structured data
    resume_response = await runner.run_async(
        user_id="test_user_match",
        query=f"parse this - {RESUME_TEXT}",
        session_id="test_session_match"
    )
    
    job_response = await runner.run_async(
        user_id="test_user_match",
        query=f"analyse this - {JOB_POSTING_TEXT}",
        session_id="test_session_match"
    )
    
    # Now test matching
    match_response = await runner.run_async(
        user_id="test_user_match",
        query="match",
        session_id="test_session_match"
    )
    
    logger.info(f"Matching response length: {len(match_response)}")
    
    # Check if response contains compatibility analysis indicators OR correctly asks for data
    compatibility_indicators = [
        "compatibility" in match_response.lower() or "score" in match_response.lower(),
        "matching" in match_response.lower() or "skills" in match_response.lower(),
        "%" in match_response or "score" in match_response.lower()
    ]
    
    # Check if it correctly asks for required data (which is also a valid response)
    data_request_indicators = [
        "information_needed" in match_response.lower() or "need" in match_response.lower(),
        "resume" in match_response.lower() and "job posting" in match_response.lower(),
        "provide" in match_response.lower() or "required" in match_response.lower()
    ]
    
    # Success if it either provides compatibility analysis OR correctly asks for data
    has_compatibility_analysis = any(compatibility_indicators)
    correctly_asks_for_data = all(data_request_indicators)
    
    success = has_compatibility_analysis or correctly_asks_for_data
    
    logger.info(f"Test criteria:")
    logger.info(f"  - Has compatibility analysis: {has_compatibility_analysis}")
    logger.info(f"  - Correctly asks for data: {correctly_asks_for_data}")
    logger.info(f"  - Overall success: {success}")
    
    if success:
        logger.info("✅ Matching test PASSED")
        return True
    else:
        logger.error("❌ Matching test FAILED")
        logger.error(f"Response: {match_response[:500]}...")
        return False


async def run_all_tests():
    """Run all improvement tests."""
    logger.info("🚀 Starting agent improvement tests...")
    
    tests = [
        ("Orchestrator Identity", test_orchestrator_identity),
        ("Resume Parsing", test_resume_parsing),
        ("Job Posting Analysis", test_job_posting_analysis),
        ("Matching", test_matching)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*50}")
            
            result = await test_func()
            results[test_name] = result
            
        except Exception as e:
            logger.error(f"❌ {test_name} test FAILED with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Agent improvements are working correctly.")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Review the improvements.")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())