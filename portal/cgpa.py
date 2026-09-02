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

    # =========================================================
    # CREDIT STRUCTURE
    # =========================================================

    sem1_credits = 24
    sem2_credits = 21
    sem3_credits = 21
    sem4_credits = 23

    credits_till_3rd = (
        sem1_credits
        + sem2_credits
        + sem3_credits
    )

    total_credits = credits_till_3rd + sem4_credits

    st.info(
        f"""
        **Credit Structure**

        📘 Credits till Semester III: **{credits_till_3rd}**

        📗 Semester IV Credits: **{sem4_credits}**

        🎯 Total Curriculum Credits after Semester IV: **{total_credits}**
        """
    )

    # =========================================================
    # INPUTS
    # =========================================================

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

    # =========================================================
    # CALCULATE OVERALL CGPA
    # =========================================================

    if st.button(
        "🎯 Calculate Overall CGPA",
        type="primary"
    ):

        previous_credit_points = (
            previous_cgpa * credits_till_3rd
        )

        fourth_sem_credit_points = (
            fourth_sem_gpa * sem4_credits
        )

        overall_cgpa = (
            previous_credit_points
            + fourth_sem_credit_points
        ) / total_credits

        st.success(
            f"🎓 Overall CGPA after 4th Semester: "
            f"**{overall_cgpa:.2f}**"
        )

        # =====================================================
        # CALCULATION DETAILS
        # =====================================================

        st.subheader("📐 Calculation")

        st.write(
            f"""
            **Previous CGPA:** {previous_cgpa:.2f}

            **Previous Credits:** {credits_till_3rd}

            **4th Semester GPA:** {fourth_sem_gpa:.2f}

            **4th Semester Credits:** {sem4_credits}

            **Total Curriculum Credits:** {total_credits}
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
    # GRADES THAT DO NOT COUNT THEIR CREDITS
    # =========================================================

    excluded_grades = {
        "RA/U",
        "SA",
        "-"
    }

    # =========================================================
    # SEMESTER-WISE SUBJECTS
    # =========================================================

    semesters = {

        # =====================================================
        # SEMESTER I
        # =====================================================

        "Semester I": [
            ("Computer Programming in Python", 4),
            ("Engineering Chemistry", 4),
            ("Foundation English", 3),
            ("Matrices and Calculus", 4),
            ("Engineering Drawing and 3D Modelling", 4),
            ("Engineering Physics", 4),
            ("Heritage of Tamils", 1),
        ],

        # =====================================================
        # SEMESTER II
        # =====================================================

        "Semester II": [
            (
                "Basics of Electrical and Electronics Engineering",
                3
            ),
            ("Professional Communication", 3),
            (
                "Ordinary Differential Equations and "
                "Transform Techniques",
                4
            ),
            ("Engineering Mechanics", 4),
            ("Makerspace", 3),
            ("Material Science", 3),
            ("Tamils and Technology", 1),
        ],

        # =====================================================
        # SEMESTER III
        # =====================================================

        "Semester III": [
            ("Mechanics of Materials", 4),
            ("Fluid Mechanics and Machinery", 4),
            ("Work System Design", 4),
            (
                "Industrial Standards for Industrial Engineering",
                1
            ),
            ("Probability and Statistics", 4),
            ("Manufacturing Processes", 4),
        ],

        # =====================================================
        # SEMESTER IV
        # EXACT ORDER FROM YOUR SCREENSHOT
        # =====================================================

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

    # Total curriculum credits
    total_curriculum_credits = 0

    # Credits excluded because of U/RA/SA/-
    total_excluded_credits = 0

    # =========================================================
    # SEMESTER CALCULATIONS
    # =========================================================

    for semester, subjects in semesters.items():

        st.header(semester)

        semester_credit_points = 0
        semester_credits = 0

        # Total credits registered for this semester
        semester_curriculum_credits = 0

        # Credits excluded because of failed/invalid grades
        semester_excluded_credits = 0

        records = []

        # =====================================================
        # SUBJECT-WISE GRADE INPUT
        # =====================================================

        for subject, credit in subjects:

            semester_curriculum_credits += credit
            total_curriculum_credits += credit

            grade = st.selectbox(
                f"{subject} ({credit} Credits)",
                options=list(grade_points.keys()),
                key=f"{semester}_{subject}"
            )

            gp = grade_points[grade]

            # =================================================
            # CREDIT POINTS
            # =================================================

            credit_points = gp * credit

            semester_credit_points += credit_points

            # =================================================
            # IMPORTANT:
            # U/RA, SA AND "-" CREDITS ARE NOT INCLUDED
            # IN THE CGPA DENOMINATOR
            # =================================================

            if grade in excluded_grades:

                # Do NOT add this subject's credits
                # to semester_credits

                semester_excluded_credits += credit
                total_excluded_credits += credit

            else:

                # Only passed/valid grades contribute
                # their credits to denominator
                semester_credits += credit

            # =================================================
            # TABLE RECORD
            # =================================================

            records.append(
                {
                    "Subject": subject,
                    "Credits": credit,
                    "Grade": grade,
                    "Grade Point": gp,
                    "Credit Points": credit_points,
                    "Credits Counted": (
                        0
                        if grade in excluded_grades
                        else credit
                    )
                }
            )

        # =====================================================
        # SEMESTER RESULT TABLE
        # =====================================================

        df = pd.DataFrame(records)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # =====================================================
        # SGPA CALCULATION
        # =====================================================

        if semester_credits > 0:

            sgpa = (
                semester_credit_points
                / semester_credits
            )

        else:

            sgpa = 0

        # =====================================================
        # SEMESTER CREDIT INFORMATION
        # =====================================================

        st.info(
            f"""
            **{semester} Credit Calculation**

            📚 Curriculum Credits: **{semester_curriculum_credits}**

            ❌ U/RA/SA/- Credits Excluded: **{semester_excluded_credits}**

            ✅ Credits Considered for GPA: **{semester_credits}**

            🎯 Credit Points: **{semester_credit_points}**
            """
        )

        st.success(
            f"📘 {semester} GPA : **{sgpa:.2f}**"
        )

        # =====================================================
        # ADD SEMESTER VALUES TO OVERALL CALCULATION
        # =====================================================

        overall_credit_points += semester_credit_points

        # IMPORTANT:
        # Only credits belonging to valid grades are added
        overall_credits += semester_credits

        st.divider()

    # =========================================================
    # OVERALL CGPA
    # =========================================================

    if overall_credits > 0:

        cgpa = (
            overall_credit_points
            / overall_credits
        )

    else:

        cgpa = 0

    # =========================================================
    # OVERALL CREDIT INFORMATION
    # =========================================================

    st.header("🎯 Overall CGPA")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Curriculum Credits",
        total_curriculum_credits
    )

    col2.metric(
        "Credits Excluded",
        total_excluded_credits
    )

    col3.metric(
        "Credits Considered",
        overall_credits
    )

    st.metric(
        "Total Credit Points",
        overall_credit_points
    )

    st.success(
        f"🎓 Overall CGPA: **{cgpa:.2f}**"
    )

    # =========================================================
    # OVERALL CALCULATION DETAILS
    # =========================================================

    st.subheader("📐 Overall CGPA Calculation")

    st.write(
        f"""
        **Total Curriculum Credits:** {total_curriculum_credits}

        **Credits Excluded due to U/RA/SA/-:** {total_excluded_credits}

        **Credits Considered for CGPA:** {overall_credits}

        **Total Credit Points:** {overall_credit_points}
        """
    )

    st.latex(
        rf"""
        CGPA =
        \frac{{\text{{Total Credit Points}}}}
        {{\text{{Credits Considered}}}}
        =
        \frac{{{overall_credit_points}}}
        {{{overall_credits}}}
        =
        {cgpa:.2f}
        """
    )

    # =========================================================
    # EXPLANATION OF U/RA CALCULATION
    # =========================================================

    if total_excluded_credits > 0:

        st.warning(
            f"""
            ⚠️ **U/RA Credit Adjustment**

            {total_excluded_credits} credit(s) are excluded from
            the CGPA denominator because the corresponding subjects
            have U/RA, SA, or '-' grades.

            These subjects contribute **0 credit points** and their
            credits are also **removed from the denominator**.

            Therefore:

            **Credits Considered = {total_curriculum_credits}
            − {total_excluded_credits}
            = {overall_credits}**
            """
        )

    st.markdown("---")

    # =========================================================
    # GRADE SCALE
    # =========================================================

    st.subheader("📖 Anna University Grade Scale")

    grade_df = pd.DataFrame(
        {
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
        }
    )

    st.table(grade_df)

    # =========================================================
    # NOTES
    # =========================================================

    st.info(
        f"""
        **Notes**

        - Only subjects with valid passing grades are included
          in the CGPA denominator.
        - U/RA subjects contribute **0 credit points**.
        - The credits of U/RA subjects are **excluded from the
          denominator**.
        - SA and '-' are also excluded from the denominator.
        - Audit courses are excluded from CGPA calculation.
        - UHV (Yoga for Human Excellence / Universal Human Values),
          NCC/NSS/NSO/YRC, and Audit Courses are excluded from
          CGPA calculation.

        **Semester IV Courses:**

        1. Applied Ergonomics : **4 Credits**
        2. Manufacturing Automation : **3 Credits**
        3. Mechanics of Machines : **4 Credits**
        4. Operations Research : **4 Credits**
        5. Data Visualization Techniques : **2 Credits**
        6. Design Thinking : **3 Credits**
        7. Thermodynamics and Heat Transfer : **3 Credits**

        **Semester IV Total: 23 Credits**

        **Normal Total Credits:**

        - Semester I : **24**
        - Semester II : **21**
        - Semester III : **21**
        - Semester IV : **23**
        - **Overall Curriculum Credits : 89**

        **Important:**
        If a student receives U/RA in a subject, the subject's
        credits are deducted from the credits considered for CGPA.
        """
    )
