#!/usr/bin/env python3
"""
Debug script to test resume parsing specifically.
"""

import asyncio
import logging
from agent_engine import get_agent_runner

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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


async def debug_resume_parsing():
    """Debug resume parsing to see what's actually returned."""
    logger.info("🔍 Debugging resume parsing...")
    runner = get_agent_runner()

    response = await runner.run_async(
        user_id="debug_user",
        query=f"parse this - {RESUME_TEXT}",
        session_id="debug_session",
    )

    logger.info(f"📏 Response length: {len(response)}")
    logger.info(f"📄 Full response:\n{response}")

    # Check what we're looking for
    checks = {
        "personal_details": "personal_details" in response,
        "work_experience": "work_experience" in response,
        "education": "education" in response,
        "skills": "skills" in response,
        "session_info": "session_info" in response,
        "full_name": "full_name" in response,
        "email": "email" in response,
        "job_title": "job_title" in response,
        "degree": "degree" in response,
        "institution": "institution" in response,
        "programming": "programming" in response,
        "competencies": "competencies" in response,
        "timestamp": "timestamp" in response,
        "operation": "operation" in response,
        "json_structure": "{" in response and "}" in response,
        "is_brief": "I am the" in response and len(response) < 200,
    }

    logger.info("🔍 Content checks:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        logger.info(f"  {status} {check}: {result}")

    return response


if __name__ == "__main__":
    asyncio.run(debug_resume_parsing())
