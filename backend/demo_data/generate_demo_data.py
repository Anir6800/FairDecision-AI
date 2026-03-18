from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


DEMO_DOCUMENTS = {
    "resume_A.pdf": [
        "Priya Sharma",
        "Location: Mumbai",
        "Education: IIT Bombay, B.Tech in Computer Science, 2018",
        "Experience:",
        "- Google, Software Engineer, 2018-01 to 2021-06",
        "- Flipkart, Senior Software Engineer, 2021-07 to PRESENT",
        "Skills: Python, Django, React, AWS",
        "Employment Gaps: None",
    ],
    "resume_B.pdf": [
        "Rahul Verma",
        "Location: Ahmedabad",
        "Education: Gujarat University, B.Tech in Computer Science, 2018",
        "Experience:",
        "- Local IT Company, Software Engineer, 2018-01 to 2021-04",
        "- Employment gap: 8 months from 2021-05 to 2021-12",
        "- Local IT Company, Senior Software Engineer, 2022-01 to PRESENT",
        "Skills: Python, Django, React, AWS",
    ],
    "resume_C.pdf": [
        "Anita Patel",
        "Location: Patan",
        "Education: State College, Diploma in Computer Engineering, 2019",
        "Experience:",
        "- Regional Software Services, Developer, 2019-07 to 2021-02",
        "- Employment gap: 14 months from 2021-03 to 2022-04",
        "- Regional Software Services, Python Developer, 2022-05 to PRESENT",
        "Skills: Python",
    ],
    "JD_senior_dev.pdf": [
        "Senior Python Developer",
        "Location: Mumbai",
        "Requirements:",
        "- Python",
        "- Django",
        "- REST APIs",
        "- 4+ years of experience",
        "- B.Tech preferred",
    ],
}


def write_pdf(path: Path, lines: list[str]) -> None:
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y_position = height - 72

    pdf.setTitle(path.stem)
    pdf.setFont("Helvetica", 12)

    for line in lines:
        if y_position < 72:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = height - 72
        pdf.drawString(72, y_position, line)
        y_position -= 20

    pdf.save()


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    for filename, lines in DEMO_DOCUMENTS.items():
        write_pdf(output_dir / filename, lines)


if __name__ == "__main__":
    main()
