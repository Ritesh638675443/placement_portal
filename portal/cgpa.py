import streamlit as st
import pandas as pd


def show_cgpa():

    st.title("🎓 INDUSTRIAL ENGINEERING CGPA Calculator")
    st.write("Anna University (R2023 Regulation)")

    # -----------------------------------
    # Grade Mapping
    # -----------------------------------
    grade_points = {
        "S": 10,
        "A+": 9,
        "A": 8,
        "B+": 7,
        "B": 6,
        "C": 5,
        "RA/U": 0,
        "SA": 0,
        "-": 0
    }

    # -----------------------------------
    # Semester-wise Subjects
    # -----------------------------------
    semesters = {

        # ===================================
        # SEMESTER I
        # ===================================
        "Semester I": [
            ("Computer Programming in Python", 4),
            ("Engineering Chemistry", 4),
            ("Foundation English", 3),
            ("Matrices and Calculus", 4),
            ("Engineering Drawing and 3D Modelling", 4),
            ("Engineering Physics", 4),
            ("Heritage of Tamils", 1),
        ],

        # ===================================
        # SEMESTER II
        # ===================================
        "Semester II": [
            ("Basics of Electrical and Electronics Engineering", 3),
            ("Professional Communication", 3),
            ("Ordinary Differential Equations and Transform Techniques", 4),
            ("Engineering Mechanics", 4),
            ("Makerspace", 3),
            ("Material Science", 3),
            ("Tamils and Technology", 1),
        ],

        # ===================================
        # SEMESTER III
        # ===================================
        "Semester III": [
            ("Mechanics of Materials", 4),
            ("Fluid Mechanics and Machinery", 4),
            ("Work System Design", 4),
            ("Industrial Standards for Industrial Engineering", 1),
            ("Probability and Statistics", 4),
            ("Manufacturing Processes", 4),
        ],

        # ===================================
        # SEMESTER IV
        # ===================================
        "Semester IV": [
            ("Applied Ergonomics", 4),
            ("Manufacturing Automation", 4),
            ("Mechanics of Machines", 3),
            ("Operations Research", 4),
            ("Data Visualization Techniques", 2),
            ("Design Thinking", 3),
            ("Thermodynamics and Heat Transfer", 3),
        ]
    }

    # -----------------------------------
    # Overall Calculation Variables
    # -----------------------------------
    overall_credit_points = 0
    overall_credits = 0

    # -----------------------------------
    # Semester Calculations
    # -----------------------------------
    for semester, subjects in semesters.items():

        st.header(semester)

        semester_credit_points = 0
        semester_credits = 0
        records = []

        for subject, credit in subjects:

            grade = st.selectbox(
                f"{subject} ({credit} Credits)",
                options=list(grade_points.keys()),
                key=f"{semester}_{subject}"
            )

            gp = grade_points[grade]
            credit_points = gp * credit

            semester_credit_points += credit_points
            semester_credits += credit

            records.append({
                "Subject": subject,
                "Credits": credit,
                "Grade": grade,
                "Grade Point": gp,
                "Credit Points": credit_points
            })

        # -----------------------------------
        # Semester Result Table
        # -----------------------------------
        df = pd.DataFrame(records)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # -----------------------------------
        # SGPA Calculation
        # -----------------------------------
        if semester_credits > 0:
            sgpa = semester_credit_points / semester_credits
        else:
            sgpa = 0

        st.success(
            f"📘 {semester} GPA : **{sgpa:.2f}**"
        )

        # Add semester values to overall calculation
        overall_credit_points += semester_credit_points
        overall_credits += semester_credits

        st.divider()

    # -----------------------------------
    # Overall CGPA Calculation
    # -----------------------------------
    if overall_credits > 0:
        cgpa = overall_credit_points / overall_credits
    else:
        cgpa = 0

    st.header("🎯 Overall CGPA")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Credits",
        overall_credits
    )

    col2.metric(
        "Total Credit Points",
        overall_credit_points
    )

    col3.metric(
        "CGPA",
        f"{cgpa:.2f}"
    )

    st.markdown("---")

    # =========================================================
    # QUICK CGPA CALCULATOR
    # =========================================================

    st.header("🧮 Calculate Overall CGPA from Previous CGPA + 4th Sem GPA")

    st.write(
        "If you already know your CGPA up to Semester III "
        "and your Semester IV GPA, you can calculate your "
        "overall CGPA directly."
    )

    # Credits based on the curriculum
    previous_credits = 24 + 21 + 21   # Sem I + II + III
    fourth_sem_credits = 23
    total_credits = previous_credits + fourth_sem_credits

    st.info(
        f"""
        **Credit Structure**

        - Credits up to Semester III: **{previous_credits}**
        - Semester IV Credits: **{fourth_sem_credits}**
        - Total Credits after Semester IV: **{total_credits}**
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        previous_cgpa = st.number_input(
            "Enter CGPA up to Semester III",
            min_value=0.00,
            max_value=10.00,
            value=0.00,
            step=0.01,
            format="%.2f",
            key="previous_cgpa"
        )

    with col2:
        fourth_sem_gpa = st.number_input(
            "Enter Semester IV GPA",
            min_value=0.00,
            max_value=10.00,
            value=0.00,
            step=0.01,
            format="%.2f",
            key="fourth_sem_gpa"
        )

    # -----------------------------------
    # Calculate Overall CGPA
    # -----------------------------------
    if st.button("Calculate Overall CGPA", type="primary"):

        previous_credit_points = previous_cgpa * previous_credits
        fourth_sem_credit_points = fourth_sem_gpa * fourth_sem_credits

        new_cgpa = (
            previous_credit_points + fourth_sem_credit_points
        ) / total_credits

        st.success(
            f"🎯 Your Overall CGPA after Semester IV is: **{new_cgpa:.2f}**"
        )

        # -----------------------------------
        # Calculation Breakdown
        # -----------------------------------
        st.subheader("📊 Calculation Breakdown")

        breakdown_df = pd.DataFrame({
            "Component": [
                "CGPA up to Semester III",
                "Semester IV GPA",
                "Credits up to Semester III",
                "Semester IV Credits",
                "Total Credits",
                "Overall CGPA"
            ],
            "Value": [
                f"{previous_cgpa:.2f}",
                f"{fourth_sem_gpa:.2f}",
                previous_credits,
                fourth_sem_credits,
                total_credits,
                f"{new_cgpa:.2f}"
            ]
        })

        st.dataframe(
            breakdown_df,
            use_container_width=True,
            hide_index=True
        )

        # -----------------------------------
        # Formula Display
        # -----------------------------------
        st.markdown("### 📐 Formula Used")

        st.latex(
            r"""
            CGPA_{new}
            =
            \frac{
            (CGPA_{old}\times Credits_{old})
            +
            (GPA_4\times Credits_4)
            }{
            Credits_{old}+Credits_4
            }
            """
        )

        st.caption(
            "The calculation is credit-weighted; the CGPA and Semester IV GPA "
            "are NOT simply averaged."
        )

    st.markdown("---")

    # -----------------------------------
    # Grade Scale
    # -----------------------------------
    st.subheader("📖 Anna University Grade Scale")

    grade_df = pd.DataFrame({
        "Letter Grade": [
            "S",
            "A+",
            "A",
            "B+",
            "B",
            "C",
            "RA/U",
            "SA",
            "-"
        ],
        "Meaning": [
            "Outstanding",
            "Excellent",
            "Very Good",
            "Good",
            "Average",
            "Satisfactory",
            "Reappear",
            "Shortage of Attendance",
            "Withheld"
        ],
        "Grade Point": [
            10,
            9,
            8,
            7,
            6,
            5,
            0,
            0,
            0
        ]
    })

    st.table(grade_df)

    # -----------------------------------
    # Notes
    # -----------------------------------
    st.info(
        """
        **Notes**

        - Only subjects included in the CGPA are considered.
        - UHV (Yoga for Human Excellence / Universal Human Values),
          NCC/NSS/NSO/YRC, and Audit Courses are **excluded from CGPA calculation**.

        **Total Credits Considered:**

        - Semester I : **24**
        - Semester II : **21**
        - Semester III : **21**
        - Semester IV : **23**
        - **Overall Credits : 89**
        """
    )
