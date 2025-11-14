import argparse
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


ProfileDict = Dict[str, object]
JobDict = Dict[str, object]


def load_profile(path: Path) -> Dict[str, object]:
    data = json.loads(path.read_text())

    name = data.get("name", "Unknown")
    skills = {skill.lower() for skill in data.get("skills", [])}
    preferences = data.get("preferences", {}) or {}
    locations = preferences.get("preferred_locations", []) or []
    roles = preferences.get("role_types", []) or []

    return {
        "name": name,
        "skills": skills,
        "locations": locations,
        "roles": roles,
    }


def load_jobs(path: Path) -> List[Dict[str, object]]:
    return json.loads(path.read_text())


def score_job(profile: Dict[str, object], job: Dict[str, object]) -> Tuple[int, Set[str]]:
    score = 0
    overlap: Set[str] = set()

    job_location = job.get("location")
    if job_location and job_location in profile.get("locations", []):
        score += 30

    job_title = job.get("title", "")
    profile_roles = profile.get("roles", []) or []
    job_title_lower = job_title.lower()
    for role in profile_roles:
        if role.lower() in job_title_lower:
            score += 30
            break

    job_technologies = {tech.lower() for tech in job.get("technologies", [])}
    profile_skills = profile.get("skills", set())
    overlap = {tech for tech in job_technologies if tech in profile_skills}
    score += 5 * len(overlap)

    return score, overlap


def rank_jobs(profile: Dict[str, object], jobs: List[Dict[str, object]]) -> List[Tuple[int, Set[str], Dict[str, object]]]:
    scored_jobs = []
    for job in jobs:
        score, overlap = score_job(profile, job)
        scored_jobs.append((score, overlap, job))
    scored_jobs.sort(key=lambda item: item[0], reverse=True)
    return scored_jobs


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank job postings against a profile")
    parser.add_argument(
        "--profile",
        type=Path,
        default=Path("aidan_resume_with_prefs.json"),
        help="Path to the profile JSON file",
    )
    parser.add_argument(
        "--jobs",
        type=Path,
        default=Path("examples/sample_jobs.json"),
        help="Path to the jobs JSON file",
    )
    args = parser.parse_args()

    profile = load_profile(args.profile)
    jobs = load_jobs(args.jobs)
    ranked_jobs = rank_jobs(profile, jobs)

    print(f"Profile loaded for: {profile['name']}")
    print("\nTop matches:\n")
    for score, overlap, job in ranked_jobs:
        title = job.get("title", "Unknown title")
        location = job.get("location", "Unknown location")
        print(f"- {title} ({location})")
        print(f"  Score: {score}")
        if overlap:
            overlap_list = ", ".join(sorted(overlap))
            print(f"  Overlap skills: {overlap_list}\n")
        else:
            print("  Overlap skills: none\n")


if __name__ == "__main__":
    main()
