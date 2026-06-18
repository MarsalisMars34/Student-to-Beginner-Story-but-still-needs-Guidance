"""
TermProject.py
==============
Project Title : Student Grade & GPA Tracker
Author        : Marsalis James
Description   : A command-line application that allows a student to manage
                courses, record grades, calculate GPA (weighted and unweighted),
                generate a transcript report, and persist all data to a JSON
                file between sessions.

Objectives demonstrated
-----------------------
1. Python syntax & data manipulation  – variables, lists, dicts, f-strings,
                                        comprehensions, string formatting
2. Control structures                 – while menus, for loops, if/elif/else,
                                        break, continue, sorted()
3. Object-Oriented Programming        – Course, Semester, and GradeBook classes
                                        with encapsulation, inheritance, and
                                        method overriding
4. Error handling                     – try/except/else/finally, custom
                                        exceptions, input validation loops
5. File handling                      – JSON save/load with json module,
                                        CSV transcript export, os.path checks
6. Libraries & modules                – json, csv, os, math, datetime,
                                        statistics, collections.defaultdict
"""

# ── Standard-library imports (Objective 6) ────────────────────────────────────
import json
import csv
import os
import math
import statistics
from datetime      import datetime
from collections   import defaultdict

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FILE       = "gradebook.json"
TRANSCRIPT_FILE = "transcript.csv"
APP_VERSION     = "1.0"

# Standard letter-grade → GPA-point mapping (4.0 scale)
GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F":  0.0,
}


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM EXCEPTION (Objective 4)
# ══════════════════════════════════════════════════════════════════════════════

class GradeBookError(Exception):
    """Raised for application-specific logical errors in the grade book."""
    pass


# ══════════════════════════════════════════════════════════════════════════════
# OOP CLASSES (Objective 3)
# ══════════════════════════════════════════════════════════════════════════════

class Course:
    """
    Represents one academic course with its grades and credit hours.

    Attributes
    ----------
    name        : str   – Course name (e.g. "Introduction to Python")
    code        : str   – Course code (e.g. "IT-101")
    credits     : int   – Credit hours (1–6)
    grades      : list  – List of (assignment_name, score, weight) tuples
    letter_grade: str   – Final letter grade (set after course is complete)
    semester    : str   – Semester this course belongs to
    """

    def __init__(self, name, code, credits, semester):
        self.name         = name
        self.code         = code.upper()
        self.credits      = int(credits)
        self.semester     = semester
        self.grades       = []          # list of dicts
        self.letter_grade = None        # set when course is finalised
        self.created_at   = datetime.now().strftime("%Y-%m-%d")

    # ── Grade management ──────────────────────────────────────────────────────

    def add_grade(self, assignment, score, max_score, weight):
        """Add one graded assignment."""
        if score < 0 or score > max_score:
            raise GradeBookError(
                f"Score {score} is out of range (0–{max_score})."
            )
        if weight <= 0 or weight > 100:
            raise GradeBookError("Weight must be between 1 and 100.")

        self.grades.append({
            "assignment": assignment,
            "score":      float(score),
            "max_score":  float(max_score),
            "weight":     float(weight),
            "date":       datetime.now().strftime("%Y-%m-%d"),
        })

    def weighted_average(self):
        """
        Return the weighted percentage average of all recorded grades.
        Formula: Σ(score/max_score * weight) / Σ(weight) * 100
        Returns 0.0 if no grades have been entered.
        """
        if not self.grades:
            return 0.0
        total_weight   = sum(g["weight"] for g in self.grades)
        weighted_score = sum(
            (g["score"] / g["max_score"]) * g["weight"]
            for g in self.grades
        )
        return (weighted_score / total_weight) * 100

    def percentage_to_letter(self):
        """Convert weighted average to a letter grade using standard brackets."""
        avg = self.weighted_average()
        if   avg >= 93: return "A"
        elif avg >= 90: return "A-"
        elif avg >= 87: return "B+"
        elif avg >= 83: return "B"
        elif avg >= 80: return "B-"
        elif avg >= 77: return "C+"
        elif avg >= 73: return "C"
        elif avg >= 70: return "C-"
        elif avg >= 67: return "D+"
        elif avg >= 63: return "D"
        elif avg >= 60: return "D-"
        else:           return "F"

    def get_gpa_points(self):
        """Return the GPA points for this course's current or final grade."""
        grade = self.letter_grade or self.percentage_to_letter()
        return GRADE_POINTS.get(grade, 0.0)

    def display(self):
        """Return a formatted one-line summary of this course."""
        avg    = self.weighted_average()
        letter = self.letter_grade or self.percentage_to_letter()
        return (
            f"  {self.code:<10} {self.name:<30} "
            f"{self.credits}cr  {avg:5.1f}%  {letter}  "
            f"({len(self.grades)} grade(s))"
        )

    def to_dict(self):
        """Serialise to a plain dictionary for JSON storage."""
        return {
            "name":         self.name,
            "code":         self.code,
            "credits":      self.credits,
            "semester":     self.semester,
            "grades":       self.grades,
            "letter_grade": self.letter_grade,
            "created_at":   self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Course object from a dictionary (used when loading)."""
        course              = cls(data["name"], data["code"],
                                  data["credits"], data["semester"])
        course.grades       = data.get("grades", [])
        course.letter_grade = data.get("letter_grade")
        course.created_at   = data.get("created_at", "")
        return course


# ── Inherited class ────────────────────────────────────────────────────────────

class HonorsCourse(Course):
    """
    A specialised Course that carries an extra 0.5 GPA-point bonus
    for honour sections (common at many universities).

    Inherits everything from Course; overrides get_gpa_points().
    """

    HONORS_BONUS = 0.5

    def __init__(self, name, code, credits, semester):
        super().__init__(name, code, credits, semester)
        self.is_honors = True   # flag so we can display it

    def get_gpa_points(self):
        """Add honors bonus (capped at 4.0 for standard scale)."""
        base = super().get_gpa_points()
        return min(4.0, base + self.HONORS_BONUS)

    def display(self):
        """Prepend [H] to indicate an honors course."""
        return "[H] " + super().display()

    def to_dict(self):
        data             = super().to_dict()
        data["is_honors"] = True
        return data


# ── Container class ────────────────────────────────────────────────────────────

class GradeBook:
    """
    Top-level container for all semesters and courses.

    Attributes
    ----------
    student_name : str
    student_id   : str
    courses      : list[Course]
    """

    def __init__(self, student_name, student_id):
        self.student_name = student_name
        self.student_id   = student_id
        self.courses      = []

    # ── Course management ─────────────────────────────────────────────────────

    def add_course(self, course):
        """Add a Course (or HonorsCourse) to the grade book."""
        # Prevent duplicate course codes within the same semester
        for c in self.courses:
            if c.code == course.code and c.semester == course.semester:
                raise GradeBookError(
                    f"Course '{course.code}' already exists in {course.semester}."
                )
        self.courses.append(course)

    def get_course(self, code, semester):
        """Find and return a course by code and semester, or None."""
        for c in self.courses:
            if c.code == code.upper() and c.semester == semester:
                return c
        return None

    def remove_course(self, code, semester):
        """Remove a course entirely."""
        course = self.get_course(code, semester)
        if not course:
            raise GradeBookError(f"Course '{code}' not found in {semester}.")
        self.courses.remove(course)

    def get_semesters(self):
        """Return a sorted list of unique semester labels."""
        return sorted(set(c.semester for c in self.courses))

    # ── GPA calculations ──────────────────────────────────────────────────────

    def cumulative_gpa(self):
        """
        Calculate cumulative GPA using the quality-points method:
            GPA = Σ(grade_points × credits) / Σ(credits)
        Only courses with at least one grade are included.
        """
        total_quality  = 0.0
        total_credits  = 0
        for c in self.courses:
            if c.grades or c.letter_grade:
                total_quality += c.get_gpa_points() * c.credits
                total_credits += c.credits
        if total_credits == 0:
            return 0.0
        return total_quality / total_credits

    def semester_gpa(self, semester):
        """Calculate GPA for one specific semester."""
        total_quality = 0.0
        total_credits = 0
        for c in self.courses:
            if c.semester == semester and (c.grades or c.letter_grade):
                total_quality += c.get_gpa_points() * c.credits
                total_credits += c.credits
        if total_credits == 0:
            return 0.0
        return total_quality / total_credits

    def total_credits_earned(self):
        """Return total credit hours from courses with a passing grade."""
        return sum(
            c.credits for c in self.courses
            if (c.letter_grade or c.percentage_to_letter()) != "F"
            and (c.grades or c.letter_grade)
        )

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self):
        return {
            "student_name": self.student_name,
            "student_id":   self.student_id,
            "courses":      [c.to_dict() for c in self.courses],
        }

    @classmethod
    def from_dict(cls, data):
        gb = cls(data["student_name"], data["student_id"])
        for cd in data.get("courses", []):
            if cd.get("is_honors"):
                course = HonorsCourse(cd["name"], cd["code"],
                                      cd["credits"], cd["semester"])
                course.grades       = cd.get("grades", [])
                course.letter_grade = cd.get("letter_grade")
                course.created_at   = cd.get("created_at", "")
            else:
                course = Course.from_dict(cd)
            gb.courses.append(course)
        return gb


# ══════════════════════════════════════════════════════════════════════════════
# TOP-LEVEL FUNCTIONS  (all at same indentation as main — Requirement)
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Input helpers (Objective 4 — error handling) ───────────────────────────

def get_string(prompt, min_len=1, max_len=80):
    """
    Prompt the user for a non-empty string within a length range.
    Loops until valid input is received.
    """
    while True:
        try:
            value = input(prompt).strip()
            if len(value) < min_len:
                raise ValueError(f"Input must be at least {min_len} character(s).")
            if len(value) > max_len:
                raise ValueError(f"Input must be {max_len} characters or fewer.")
            return value
        except ValueError as e:
            print(f"  [Error] {e}")


def get_float(prompt, min_val=0.0, max_val=float("inf")):
    """Prompt for a float within [min_val, max_val]. Loops until valid."""
    while True:
        try:
            value = float(input(prompt))
            if value < min_val or value > max_val:
                raise ValueError(f"Value must be between {min_val} and {max_val}.")
            return value
        except ValueError as e:
            print(f"  [Error] {e}  Please try again.")


def get_int(prompt, min_val=1, max_val=100):
    """Prompt for an integer within [min_val, max_val]. Loops until valid."""
    while True:
        try:
            value = int(input(prompt))
            if value < min_val or value > max_val:
                raise ValueError(f"Value must be between {min_val} and {max_val}.")
            return value
        except ValueError as e:
            print(f"  [Error] {e}  Please try again.")


def get_choice(prompt, valid_options):
    """Prompt for a menu choice from a known set. Loops until valid."""
    while True:
        choice = input(prompt).strip().upper()
        if choice in [o.upper() for o in valid_options]:
            return choice
        print(f"  [Error] Please enter one of: {', '.join(valid_options)}")


# ── 2. File I/O (Objective 5) ─────────────────────────────────────────────────

def save_data(gradebook, filename=DATA_FILE):
    """
    Persist the entire GradeBook to a JSON file.
    Creates the file if it does not exist; overwrites if it does.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(gradebook.to_dict(), f, indent=4)
        print(f"\n  Data saved to '{filename}'.")
    except PermissionError:
        print(f"  [Error] No write permission for '{filename}'.")
    except OSError as e:
        print(f"  [Error] Could not save data: {e}")
    finally:
        # Finally block always runs — useful for confirming the operation ended
        print("  Save operation complete.")


def load_data(filename=DATA_FILE):
    """
    Load GradeBook data from a JSON file.
    Returns a new GradeBook object, or None if the file does not exist.
    """
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return GradeBook.from_dict(data)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [Warning] Could not read save file: {e}")
        print("  Starting with a new grade book.")
        return None
    except OSError as e:
        print(f"  [Error] File access error: {e}")
        return None


def export_transcript(gradebook, filename=TRANSCRIPT_FILE):
    """
    Export a CSV transcript of all courses.
    Columns: Semester, Code, Name, Credits, Avg%, LetterGrade, GPA_Points
    """
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header row
            writer.writerow([
                "Semester", "Code", "Course Name",
                "Credits", "Avg %", "Letter Grade", "GPA Points"
            ])
            for semester in gradebook.get_semesters():
                for c in gradebook.courses:
                    if c.semester == semester:
                        letter = c.letter_grade or c.percentage_to_letter()
                        writer.writerow([
                            semester,
                            c.code,
                            c.name,
                            c.credits,
                            f"{c.weighted_average():.2f}",
                            letter,
                            f"{c.get_gpa_points():.1f}",
                        ])
            # Summary rows
            writer.writerow([])
            writer.writerow(["Cumulative GPA", "", "", "", "",
                              "", f"{gradebook.cumulative_gpa():.3f}"])
            writer.writerow(["Total Credits", "", "", "",
                              gradebook.total_credits_earned(), "", ""])
        print(f"\n  Transcript exported to '{filename}'.")
    except OSError as e:
        print(f"  [Error] Could not export transcript: {e}")


# ── 3. Display / reporting (Objectives 1 & 2) ─────────────────────────────────

def display_gradebook(gradebook):
    """
    Print a full, semester-by-semester view of the grade book
    including per-semester GPA and cumulative GPA.
    """
    if not gradebook.courses:
        print("\n  No courses recorded yet.")
        return

    print(f"\n{'═' * 72}")
    print(f"  GRADE BOOK — {gradebook.student_name}  (ID: {gradebook.student_id})")
    print(f"{'═' * 72}")

    for semester in gradebook.get_semesters():
        sem_courses = [c for c in gradebook.courses if c.semester == semester]
        print(f"\n  ── {semester} {'─' * (55 - len(semester))}")
        print(f"  {'Code':<10} {'Course Name':<30} {'Cr':>2}  {'Avg%':>5}  "
              f"{'Ltr':>3}  {'Grades':>7}")
        print(f"  {'─'*68}")

        for course in sorted(sem_courses, key=lambda c: c.code):
            print(course.display())

        sgpa = gradebook.semester_gpa(semester)
        sem_cr = sum(c.credits for c in sem_courses if c.grades or c.letter_grade)
        print(f"\n  Semester GPA: {sgpa:.3f}   |   Credit hours: {sem_cr}")

    print(f"\n{'─' * 72}")
    cgpa = gradebook.cumulative_gpa()
    total_cr = gradebook.total_credits_earned()
    print(f"  Cumulative GPA : {cgpa:.3f}   |   Total credits earned: {total_cr}")
    # Use statistics module to show GPA standing
    standing = gpa_standing(cgpa)
    print(f"  Academic Standing: {standing}")
    print(f"{'═' * 72}\n")


def display_course_detail(course):
    """Print all grade entries for a single course."""
    print(f"\n{'─' * 60}")
    print(f"  {course.code} — {course.name}  ({course.credits} credits, {course.semester})")
    if getattr(course, "is_honors", False):
        print("  [Honors section — +0.5 GPA bonus]")
    print(f"{'─' * 60}")

    if not course.grades:
        print("  No grades recorded yet.")
    else:
        print(f"  {'Assignment':<28} {'Score':>6}  {'Max':>6}  "
              f"{'Wt%':>4}  {'Earned%':>7}")
        print(f"  {'─'*56}")
        for g in course.grades:
            earned = (g["score"] / g["max_score"]) * 100
            print(f"  {g['assignment']:<28} {g['score']:>6.1f}  "
                  f"{g['max_score']:>6.1f}  {g['weight']:>4.0f}%  {earned:>6.1f}%")

    print(f"\n  Weighted Average : {course.weighted_average():.2f}%")
    print(f"  Letter Grade     : {course.letter_grade or course.percentage_to_letter()}")
    print(f"  GPA Points       : {course.get_gpa_points():.1f}")
    print(f"{'─' * 60}\n")


# ── 4. Analytics (Objectives 1, 2, 6) ────────────────────────────────────────

def gpa_standing(gpa):
    """
    Return an academic standing label for a given GPA.
    Uses if/elif/else control structure.
    """
    if   gpa >= 3.9: return "Summa Cum Laude  (≥ 3.9)"
    elif gpa >= 3.7: return "Magna Cum Laude  (≥ 3.7)"
    elif gpa >= 3.5: return "Cum Laude        (≥ 3.5)"
    elif gpa >= 3.0: return "Good Standing    (≥ 3.0)"
    elif gpa >= 2.0: return "Satisfactory     (≥ 2.0)"
    elif gpa >  0.0: return "Academic Warning (< 2.0)"
    else:            return "No GPA recorded"


def analyze_performance(gradebook):
    """
    Generate a statistical performance report using the statistics module.
    Shows:
      • Best and worst performing courses
      • Average GPA across all semesters
      • Spending distribution by semester (defaultdict)
      • GPA trend: improving, declining, or stable
    """
    if not gradebook.courses:
        print("\n  No data to analyze.")
        return

    # Collect all course averages that have at least one grade
    averages = [
        (c.name, c.weighted_average())
        for c in gradebook.courses
        if c.grades
    ]

    if not averages:
        print("\n  No grades recorded yet.")
        return

    scores = [avg for _, avg in averages]
    best   = max(averages, key=lambda x: x[1])
    worst  = min(averages, key=lambda x: x[1])

    print(f"\n{'═' * 60}")
    print("  PERFORMANCE ANALYTICS")
    print(f"{'═' * 60}")
    print(f"  Best course  : {best[0]}  ({best[1]:.1f}%)")
    print(f"  Worst course : {worst[0]}  ({worst[1]:.1f}%)")
    print(f"  Mean average : {statistics.mean(scores):.2f}%")

    # Only compute stdev with 2+ values
    if len(scores) >= 2:
        print(f"  Std deviation: {statistics.stdev(scores):.2f}%")

    # Per-semester GPA using defaultdict to accumulate quality points
    sem_quality  = defaultdict(float)
    sem_credits  = defaultdict(int)
    for c in gradebook.courses:
        if c.grades or c.letter_grade:
            sem_quality[c.semester]  += c.get_gpa_points() * c.credits
            sem_credits[c.semester]  += c.credits

    print(f"\n  {'Semester':<20} {'GPA':>6}")
    print(f"  {'─'*28}")
    sem_gpas = []
    for sem in sorted(sem_quality):
        sgpa = sem_quality[sem] / sem_credits[sem] if sem_credits[sem] else 0
        sem_gpas.append(sgpa)
        print(f"  {sem:<20} {sgpa:>6.3f}")

    # Trend analysis using math.isclose and list comparison
    if len(sem_gpas) >= 2:
        delta = sem_gpas[-1] - sem_gpas[0]
        if math.isclose(delta, 0, abs_tol=0.05):
            trend = "Stable"
        elif delta > 0:
            trend = f"Improving (+{delta:.3f})"
        else:
            trend = f"Declining ({delta:.3f})"
        print(f"\n  GPA Trend: {trend}")

    # Credits needed for common degree milestones
    earned = gradebook.total_credits_earned()
    for milestone, label in [(60, "Associate's"), (120, "Bachelor's")]:
        remaining = max(0, milestone - earned)
        if remaining > 0:
            print(f"\n  Credits toward {label} ({milestone} total): "
                  f"{earned} earned, {remaining} remaining.")
        else:
            print(f"\n  {label}'s degree credit requirement ({milestone}) MET.")

    print(f"{'═' * 60}\n")


# ── 5. Menu sub-sections (Objective 2 — control structures) ───────────────────

def menu_add_course(gradebook):
    """Interactively add a new course to the grade book."""
    print("\n── Add Course ──────────────────────────────────────")
    name     = get_string("Course name     : ")
    code     = get_string("Course code     : ", max_len=10)
    credits  = get_int   ("Credit hours (1-6): ", min_val=1, max_val=6)
    semester = get_string("Semester (e.g. Fall 2026): ")
    honors   = get_choice("Honors section? (Y/N): ", ["Y", "N"])

    try:
        if honors == "Y":
            course = HonorsCourse(name, code, credits, semester)
        else:
            course = Course(name, code, credits, semester)
        gradebook.add_course(course)
        print(f"\n  Course '{code.upper()}' added to {semester}.")
    except GradeBookError as e:
        print(f"  [Error] {e}")


def menu_add_grade(gradebook):
    """Interactively add a grade to an existing course."""
    if not gradebook.courses:
        print("\n  No courses found. Add a course first.")
        return

    print("\n── Add Grade ───────────────────────────────────────")
    semester = get_string("Semester: ")
    code     = get_string("Course code: ").upper()

    course = gradebook.get_course(code, semester)
    if not course:
        print(f"  [Error] Course '{code}' not found in {semester}.")
        return

    assignment = get_string("Assignment name : ")
    score      = get_float ("Score earned    : ", min_val=0)
    max_score  = get_float ("Maximum score   : ", min_val=1)
    weight     = get_float ("Weight (%)      : ", min_val=0.1, max_val=100)

    try:
        course.add_grade(assignment, score, max_score, weight)
        print(f"  Grade added. Current average: {course.weighted_average():.2f}%")
    except GradeBookError as e:
        print(f"  [Error] {e}")


def menu_view_course(gradebook):
    """Display detailed grade breakdown for a single course."""
    if not gradebook.courses:
        print("\n  No courses found.")
        return

    print("\n── View Course Detail ──────────────────────────────")
    semester = get_string("Semester: ")
    code     = get_string("Course code: ").upper()

    course = gradebook.get_course(code, semester)
    if course:
        display_course_detail(course)
    else:
        print(f"  [Error] Course '{code}' not found in {semester}.")


def menu_finalize_grade(gradebook):
    """Override the calculated grade with a final official letter grade."""
    print("\n── Finalize Letter Grade ───────────────────────────")
    semester = get_string("Semester: ")
    code     = get_string("Course code: ").upper()
    course   = gradebook.get_course(code, semester)

    if not course:
        print(f"  [Error] Course '{code}' not found in {semester}.")
        return

    valid_grades = list(GRADE_POINTS.keys())
    print(f"  Valid grades: {', '.join(valid_grades)}")
    letter = get_string("Final letter grade: ").upper()

    if letter not in GRADE_POINTS:
        print(f"  [Error] '{letter}' is not a recognised grade.")
        return

    course.letter_grade = letter
    print(f"  Final grade for {code} set to {letter} "
          f"({GRADE_POINTS[letter]:.1f} GPA points).")


def menu_remove_course(gradebook):
    """Remove a course from the grade book."""
    print("\n── Remove Course ───────────────────────────────────")
    semester = get_string("Semester: ")
    code     = get_string("Course code: ").upper()

    confirm = get_choice(
        f"  Remove '{code}' from {semester}? This cannot be undone. (Y/N): ",
        ["Y", "N"]
    )
    if confirm == "N":
        print("  Cancelled.")
        return

    try:
        gradebook.remove_course(code, semester)
        print(f"  Course '{code}' removed.")
    except GradeBookError as e:
        print(f"  [Error] {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Application entry point.
    Handles first-time setup, loads saved data, and drives the main menu loop.
    """
    print(f"\n{'═' * 60}")
    print(f"  Student Grade & GPA Tracker  v{APP_VERSION}")
    print(f"  {datetime.now().strftime('%A, %B %d, %Y  %I:%M %p')}")
    print(f"{'═' * 60}\n")

    # ── Load or initialise grade book (Objective 5) ───────────────────────────
    gradebook = load_data()

    if gradebook is None:
        print("  Welcome! Let's set up your grade book.\n")
        student_name = get_string("Your full name   : ")
        student_id   = get_string("Student ID / email: ")
        gradebook    = GradeBook(student_name, student_id)
        print(f"\n  Grade book created for {student_name}.\n")
    else:
        print(f"  Welcome back, {gradebook.student_name}!")
        print(f"  Loaded {len(gradebook.courses)} course(s)  |  "
              f"Cumulative GPA: {gradebook.cumulative_gpa():.3f}\n")

    # ── Main menu loop (Objective 2) ──────────────────────────────────────────
    MENU = {
        "1": "View Full Grade Book",
        "2": "Add Course",
        "3": "Add Grade to Course",
        "4": "View Course Detail",
        "5": "Finalize Letter Grade",
        "6": "Remove Course",
        "7": "Performance Analytics",
        "8": "Export Transcript (CSV)",
        "9": "Save & Quit",
    }

    while True:
        print(f"\n{'─' * 40}")
        print(f"  MAIN MENU  —  {gradebook.student_name}")
        print(f"{'─' * 40}")
        for key, label in MENU.items():
            print(f"  {key}. {label}")
        print(f"{'─' * 40}")

        choice = get_choice("  Choice: ", list(MENU.keys()))

        if   choice == "1": display_gradebook(gradebook)
        elif choice == "2": menu_add_course(gradebook)
        elif choice == "3": menu_add_grade(gradebook)
        elif choice == "4": menu_view_course(gradebook)
        elif choice == "5": menu_finalize_grade(gradebook)
        elif choice == "6": menu_remove_course(gradebook)
        elif choice == "7": analyze_performance(gradebook)
        elif choice == "8": export_transcript(gradebook)
        elif choice == "9":
            save_data(gradebook)
            print(f"\n  Goodbye, {gradebook.student_name}!\n")
            break


# ── Guard: only run main() when this file is executed directly ────────────────
if __name__ == "__main__":
    main()
