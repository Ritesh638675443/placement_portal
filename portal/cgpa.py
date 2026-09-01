import streamlit as st
import pandas as pd


def show_cgpa():

    st.title("🎓 INDUSTRIAL ENGINEERING CGPA Calculator")
    st.write("Anna University (R2023 Regulation)")

    # =========================================================
    # QUICK CGPA CALCULATOR
    # =========================================================

    st.header("🧮 Overall CGPA Calculator")

    st.write(
        "Enter your CGPA up to Semester III and your Semester IV GPA "
        "to calculate your overall CGPA."
    )

    # Credit structure
    sem1_credits = 24
    sem2_credits = 21
    sem3_credits = 21
    sem4_credits = 23

    credits_till_3rd = sem1_credits + sem2_credits + sem3_credits
    total_credits = credits_till_3rd + sem4_credits

    st.info(
        f"""
        **Credit Structure**

        📘 Credits till Semester III: **{credits_till_3rd}**

        📗 Semester IV Credits: **{sem4_credits}**

        🎯 Total Credits after Semester IV: **{total_credits}**
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        previous_cgpa = st.number_input(
            "📊 CGPA Till 3rd Semester",
            min_value=0.00,
            max_value=10.00,
            value=0.00,
            step=0.01,
            format="%.2f",
            key="quick_previous_cgpa"
        )

    with col2:
        fourth_sem_gpa = st.number_input(
            "📘 4th Semester GPA",
            min_value=0.00,
            max_value=10.00,
            value=0.00,
            step=0.01,
            format="%.2f",
            key="quick_fourth_gpa"
        )

    if st.button("🎯 Calculate Overall CGPA", type="primary"):

        # Credit-weighted calculation
        previous_credit_points = previous_cgpa * credits_till_3rd
        fourth_sem_credit_points = fourth_sem_gpa * sem4_credits

        overall_cgpa = (
            previous_credit_points + fourth_sem_credit_points
        ) / total_credits

        st.success(
            f"🎓 Overall CGPA after 4th Semester: **{overall_cgpa:.2f}**"
        )

        # Calculation details
        st.subheader("📐 Calculation")

        st.write(
            f"""
            **Previous CGPA:** {previous_cgpa:.2f}

            **Previous Credits:** {credits_till_3rd}

            **4th Semester GPA:** {fourth_sem_gpa:.2f}

            **4th Semester Credits:** {sem4_credits}
            """
        )

        st.latex(
            rf"""
            CGPA =
            \frac{{({previous_cgpa:.2f}\times{credits_till_3rd})
            +({fourth_sem_gpa:.2f}\times{sem4_credits})}}
            {{{total_credits}}}
            =
            {overall_cgpa:.2f}
            """
        )

    st.markdown("---")

    # =========================================================
    # GRADE MAPPING
    # =========================================================

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

    # =========================================================
    # SEMESTER-WISE SUBJECTS
    # =========================================================

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
            ("Manufacturing Automation", 3),
            ("Mechanics of Machines", 4),
            ("Operations Research", 4),
            ("Data Visualization Techniques", 2),
            ("Design Thinking", 3),
            ("Thermodynamics and Heat Transfer", 3),
        ]
    }

    # =========================================================
    # OVERALL CALCULATION VARIABLES
    # =========================================================

    overall_credit_points = 0
    overall_credits = 0

    # =========================================================
    # SEMESTER CALCULATIONS
    # =========================================================

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

    # =========================================================
    # OVERALL CGPA
    # =========================================================

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
    # GRADE SCALE
    # =========================================================

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

    # =========================================================
    # NOTES
    # =========================================================

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
