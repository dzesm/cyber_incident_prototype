import os
import tempfile

import streamlit as st

from src.evidence import EvidenceResult
from src.phishing_model import PhishingModel
from src.screenshot_analyser import ScreenshotAnalyser
from src.log_analyser import LogAnalyser
from src.orchestrator import IncidentOrchestrator
from src.llm_report_generator import LLMReportGenerator


st.set_page_config(
    page_title="AI Cyber Incident Intelligence",
    layout="wide",
)


# -------------------------------------------------
# Load models once
# -------------------------------------------------

@st.cache_resource
def load_components():

    return {
        "phishing":
            PhishingModel(),

        "screenshot":
            ScreenshotAnalyser(),

        "log":
            LogAnalyser(),

        "orchestrator":
            IncidentOrchestrator(),

        "report_generator":
            LLMReportGenerator(),
    }


components = load_components()


# -------------------------------------------------
# Page
# -------------------------------------------------

st.title(
    "AI-Assisted Cybersecurity "
    "Incident Intelligence System"
)

st.write(
    "Analyse multiple cybersecurity evidence "
    "sources and combine their findings into "
    "a structured incident intelligence report."
)


# -------------------------------------------------
# Evidence inputs
# -------------------------------------------------

email_tab, screenshot_tab, log_tab = st.tabs(
    [
        "Suspicious Email",
        "Screenshot",
        "Security Logs",
    ]
)


with email_tab:

    email_text = st.text_area(
        "Paste email evidence:",
        height=250,
        placeholder=(
            "Paste a suspicious or legitimate "
            "email here..."
        ),
    )


with screenshot_tab:

    uploaded_image = st.file_uploader(
        "Upload screenshot evidence",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
    )

    if uploaded_image is not None:

        st.image(
            uploaded_image,
            caption="Submitted screenshot evidence",
            width=700,
        )


with log_tab:

    log_text = st.text_area(
        "Paste structured HDFS log events:",
        height=250,
        placeholder=(
            "Example: E22 E5 E5 E26 "
            "E11 E9 E11..."
        ),
    )


# -------------------------------------------------
# Analyse incident
# -------------------------------------------------

st.divider()

if st.button(
    "Analyse Incident",
    type="primary",
):

    evidence_items = []

    # =============================================
    # EMAIL
    # =============================================

    if email_text.strip():

        with st.spinner(
            "Analysing email..."
        ):

            email_result = (
                components["phishing"].analyse(
                    email_text
                )
            )

        evidence_items.append(
            EvidenceResult(
                source_type="email",

                classification=
                    email_result[
                        "classification"
                    ],

                confidence=
                    email_result[
                        "confidence"
                    ],

                indicators=[
                    (
                        "AI phishing probability: "
                        f"{email_result['phishing_probability']:.2%}"
                    )
                ],

                details=email_result,
            )
        )

    # =============================================
    # SCREENSHOT
    # =============================================

    if uploaded_image is not None:

        suffix = os.path.splitext(
            uploaded_image.name
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(
                uploaded_image.getbuffer()
            )

            temp_path = temp_file.name

        try:

            with st.spinner(
                "Extracting and analysing "
                "screenshot..."
            ):

                screenshot_result = (
                    components[
                        "screenshot"
                    ].analyse(
                        temp_path
                    )
                )

            phishing_analysis = (
                screenshot_result[
                    "phishing_analysis"
                ]
            )

            ocr_result = (
                screenshot_result["ocr"]
            )

            evidence_items.append(
                EvidenceResult(
                    source_type="screenshot",

                    classification=
                        phishing_analysis[
                            "classification"
                        ],

                    confidence=
                        phishing_analysis[
                            "confidence"
                        ],

                    indicators=[
                        (
                            "OCR confidence: "
                            f"{ocr_result['average_confidence']:.2%}"
                        ),
                        (
                            "Screenshot phishing "
                            "probability: "
                            f"{phishing_analysis['phishing_probability']:.2%}"
                        ),
                    ],

                    details={
                        "ocr":
                            ocr_result,

                        "phishing_analysis":
                            phishing_analysis,
                    },
                )
            )

        finally:

            if os.path.exists(
                temp_path
            ):
                os.remove(
                    temp_path
                )

    # =============================================
    # SECURITY LOG
    # =============================================

    if log_text.strip():

        with st.spinner(
            "Analysing security logs..."
        ):

            log_result = (
                components["log"].analyse(
                    log_text
                )
            )

        evidence_items.append(
            EvidenceResult(
                source_type=
                    "security_log",

                classification=
                    log_result[
                        "classification"
                    ],

                confidence=
                    log_result[
                        "confidence"
                    ],

                indicators=[
                    (
                        "Log anomaly probability: "
                        f"{log_result['anomaly_probability']:.2%}"
                    ),
                    (
                        "Events analysed: "
                        f"{log_result['event_count']}"
                    ),
                ],

                details=log_result,
            )
        )

    # =============================================
    # NO EVIDENCE
    # =============================================

    if not evidence_items:

        st.warning(
            "Please provide at least one "
            "evidence source."
        )

        st.stop()

    # =============================================
    # ORCHESTRATION
    # =============================================

    incident_context = (
        components[
            "orchestrator"
        ].combine(
            evidence_items
        )
    )


    # =============================================
    # RESULTS
    # =============================================

    st.header(
        "Incident Analysis"
    )

    col1, col2, col3 = st.columns(
        3
    )

    col1.metric(
        "Evidence Sources",
        incident_context[
            "evidence_count"
        ],
    )

    col2.metric(
        "Suspicious Sources",
        incident_context[
            "suspicious_evidence_count"
        ],
    )

    col3.metric(
        "Incident Severity",
        incident_context[
            "severity"
        ],
    )


    # ---------------------------------------------
    # Individual evidence
    # ---------------------------------------------

    st.subheader(
        "Evidence Analysis"
    )

    for evidence in evidence_items:

        with st.expander(
            evidence.source_type
            .replace("_", " ")
            .title()
        ):

            st.write(
                "**Classification:**",
                evidence.classification,
            )

            if evidence.confidence is not None:

                st.write(
                    "**Confidence:**",
                    f"{evidence.confidence:.2%}",
                )

            for indicator in (
                evidence.indicators
            ):

                st.write(
                    f"- {indicator}"
                )


    # =============================================
    # LLM REPORT
    # =============================================

    st.subheader(
        "Incident Intelligence Report"
    )

    try:

        with st.spinner(
            "Generating incident report..."
        ):

            report = (
                components[
                    "report_generator"
                ].generate(
                    incident_context
                )
            )

        st.write(
            report
        )

        st.download_button(
            label="Download Report",
            data=report,
            file_name=(
                "incident_intelligence_report.txt"
            ),
            mime="text/plain",
        )

    except Exception as error:

        st.error(
            "The evidence analysis completed, "
            "but the LLM report could not be "
            "generated."
        )

        st.exception(
            error
        )