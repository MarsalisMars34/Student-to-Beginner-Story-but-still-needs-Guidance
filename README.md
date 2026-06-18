# Student Grade & GPA Tracker

#### Video Demo: <URL here>

#### Description:

## What This Project Does

The **Student Grade & GPA Tracker** is a fully interactive command-line application written in Python that allows a student to manage their entire academic record from one program. Instead of manually tracking grades in a spreadsheet or relying on a university portal that may not always be accessible, this application puts the student in complete control of their own academic data.

When launched for the first time, the application asks for the student's name and ID, then creates a personal grade book. On every subsequent launch, the grade book is automatically loaded from a saved JSON file, so no data is ever lost between sessions.

From the main menu, the student can:

- **Add courses** — including regular and honors sections — for any semester (e.g., "Fall 2026", "Spring 2027").
- **Record grades** for individual assignments, exams, and projects. Each grade entry stores the assignment name, the score earned, the maximum possible score, and the weight of that assignment toward the overall course grade.
- **Calculate weighted averages** for every course automatically. The weighted average formula accounts for the fact that a final exam worth 40% of a grade should count more than a homework assignment worth 5%.
- **View a full grade book** — organized by semester — showing each course's current average, letter grade, and GPA points on a 4.0 scale.
- **Track cumulative GPA** and per-semester GPA using the quality-points method, which is the same calculation used by most accredited colleges and universities.
- **Analyze performance** using descriptive statistics including mean, standard deviation, best and worst courses, GPA trend over semesters, and credits remaining toward an Associate's or Bachelor's degree.
- **Finalize letter grades** — if a professor posts an official final grade that differs from the calculated average, the student can override the computed grade with the official one.
- **Export a CSV transcript** — a formatted spreadsheet-compatible file that lists every course, its grade, and its GPA points, along with a cumulative summary at the bottom.
- **Save and load data** — the grade book is saved to a local `gradebook.json` file every time the student chooses to exit, and reloaded automatically on the next run.

---

## Files in This Project

### `TermProject.py`

This is the main application file. It contains all program logic, structured as follows:

**Classes (Object-Oriented Programming):**
- `GradeBookError` — A custom exception class used to signal application-level errors (such as a duplicate course code or an invalid score) without crashing the program.
- `Course` — Represents a single academic course. Stores the course name, code, credit hours, semester, a list of grade entries, and an optional final letter grade. Provides methods to calculate the weighted average, convert it to a letter grade, retrieve GPA points, and serialize the object to a dictionary for JSON storage.
- `HonorsCourse` — Inherits from `Course` and adds a 0.5 GPA-point honors bonus. Overrides the `get_gpa_points()` and `display()` methods to reflect the honors distinction. This demonstrates inheritance and method overriding.
- `GradeBook` — The top-level container. Stores the student's name, ID, and a list of all `Course` objects. Provides methods for adding, retrieving, and removing courses, calculating cumulative and per-semester GPA, and serializing the entire grade book to and from a dictionary.

**Top-level functions (all defined at the same indentation level as `main`):**
- `get_string()`, `get_float()`, `get_int()`, `get_choice()` — Input validation helpers. Each uses a `while True` loop with `try/except` to block invalid input and display friendly error messages until the user provides a valid value.
- `save_data()` — Saves the GradeBook to a JSON file using `json.dump()`. Handles `PermissionError` and `OSError`. Includes a `finally` block to confirm the save operation completed.
- `load_data()` — Reads the JSON file using `json.load()` and reconstructs the GradeBook object. Handles `json.JSONDecodeError` and `KeyError` gracefully, starting fresh instead of crashing.
- `export_transcript()` — Writes a CSV transcript using Python's built-in `csv.writer`. Includes a header row, one row per course, and summary rows for cumulative GPA and total credits.
- `display_gradebook()` — Prints a formatted, semester-organized view of all courses. Uses `for` loops, `if/elif/else`, and f-string column alignment.
- `display_course_detail()` — Prints a detailed breakdown of all grade entries for a single course, including each assignment's earned percentage.
- `gpa_standing()` — Converts a numeric GPA to an academic standing label (e.g., "Magna Cum Laude", "Good Standing") using an `if/elif/else` chain.
- `analyze_performance()` — Generates a statistical performance report using the `statistics` module (mean, standard deviation), `collections.defaultdict` for per-semester aggregation, `math.isclose()` for trend detection, and logical comparisons to identify credit milestones.
- `menu_add_course()`, `menu_add_grade()`, `menu_view_course()`, `menu_finalize_grade()`, `menu_remove_course()` — Interactive sub-menu handlers that collect user input, call the appropriate GradeBook methods, and handle any `GradeBookError` exceptions.
- `main()` — The application entry point. Loads saved data (or runs first-time setup), then drives the main `while True` menu loop.

### `requirements.txt`

Lists all Python modules used by the project. Every module in this project (`json`, `csv`, `os`, `math`, `statistics`, `datetime`, `collections`) is part of the Python Standard Library, so no third-party installation via `pip` is required. The file is included to satisfy the submission requirement and to document the project's dependencies explicitly.

### `gradebook.json` (auto-generated at runtime)

Created automatically the first time the user exits the application. This file stores the complete grade book — student name, student ID, all courses, all grades, and all letter grades — in JSON format. It is read back in on every subsequent launch. This file should not be manually edited unless the user understands the JSON structure.

### `transcript.csv` (generated on demand)

Created when the user selects "Export Transcript (CSV)" from the main menu. This file can be opened in Microsoft Excel, Google Sheets, or any spreadsheet application. It contains one row per course with semester, course code, name, credit hours, average percentage, letter grade, and GPA points, followed by summary rows for cumulative GPA and total credits earned.

---

## Design Decisions

### Why a command-line interface instead of a GUI?

A CLI was chosen deliberately to keep the project focused on demonstrating core Python fundamentals — syntax, control structures, OOP, error handling, file I/O, and libraries — without introducing the complexity of a GUI framework like Tkinter. A well-structured CLI application with clean menus and input validation demonstrates these skills more clearly and is also easier to run across different operating systems without additional dependencies.

### Why JSON for data storage instead of CSV or a database?

JSON was chosen because it naturally represents nested data structures. A grade book contains semesters, which contain courses, which contain lists of grade entries — this hierarchy maps directly to JSON objects and arrays. CSV is flat (tabular), which would require multiple files or a complex flat format to represent the same data. A full database (like SQLite) would add complexity beyond what is needed for a personal single-user tool.

### Why a custom `GradeBookError` exception?

Rather than relying on Python's built-in exceptions (like `ValueError`) for application logic errors, a custom `GradeBookError` exception makes the code more readable and specific. When a `GradeBookError` is caught in a menu function, it is immediately clear that the error is a business logic error (such as a duplicate course), not a raw Python type error.

### Why separate `HonorsCourse` as a child class instead of a flag on `Course`?

Using inheritance makes the honors behavior explicit and extensible. A simple boolean flag on `Course` would require `if` statements scattered throughout the code. With `HonorsCourse`, all honors-specific logic (the GPA bonus, the display label) lives in one class that can be extended independently without modifying `Course`. This demonstrates the Open/Closed Principle — the `Course` class is open for extension but does not need to be modified.

### Why use `statistics.stdev()` instead of calculating manually?

The `statistics` module is part of Python's standard library and is the recommended way to perform statistical calculations. Using it demonstrates the value of Python's built-in modules (Objective 6) and produces more readable, maintainable code than a manual standard deviation formula would.

---

## How to Run

1. Ensure Python 3.10 or later is installed.
2. Place `TermProject.py` and `requirements.txt` in the same folder.
3. Open a terminal in that folder and run:

```bash
python TermProject.py
```

4. On first launch, enter your name and student ID when prompted.
5. Use the numbered menu to add courses, record grades, and view your GPA.
6. Select option 9 to save and exit. Your data will be reloaded automatically next time.

---

*Project developed for Python 1 — IT/CS Program*
*Author: Marsalis James*
