import argparse
import difflib
import json
import re
from pathlib import Path

MATCH_THRESHOLD = 0.4

STOPWORDS = {
    "a", "an", "the", "to", "for", "and", "or", "of", "in", "on", "at", "by",
    "with", "from", "is", "are", "be", "this", "that", "it", "its", "as",
}

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}

FILLER_PHRASES = ["end of day", "today", "tomorrow"]

ORDINAL_RE = re.compile(r"^(\d+)(?:st|nd|rd|th)?$")


def words(text):
    return set(re.findall(r"[a-z0-9']+", text.lower())) - STOPWORDS


def word_overlap(a, b):
    wa, wb = words(a), words(b)
    if not wa and not wb:
        return 1.0
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def task_similarity(a, b):
    seq_ratio = difflib.SequenceMatcher(None, a, b).ratio()
    return max(seq_ratio, word_overlap(a, b))


def parse_month_day(date_str):
    if date_str is None:
        return None, None
    s = date_str.lower()
    for phrase in FILLER_PHRASES:
        s = s.replace(phrase, " ")

    month = None
    for name, num in MONTHS.items():
        if re.search(rf"\b{name}\b", s):
            month = num
            break

    day = None
    for raw_word in re.split(r"[^a-z0-9]+", s):
        if not raw_word or raw_word in WEEKDAYS or raw_word in MONTHS:
            continue
        m = ORDINAL_RE.match(raw_word)
        if m:
            day = int(m.group(1))
            break

    return month, day


def owners_equal(pred_owner, key_owner):
    if pred_owner is None and key_owner is None:
        return True
    if pred_owner is None or key_owner is None:
        return False
    return pred_owner.strip().lower() == key_owner.strip().lower()


def due_dates_equal(pred_date, key_date):
    if pred_date is None and key_date is None:
        return True
    if pred_date is None or key_date is None:
        return False
    key_month, key_day = parse_month_day(key_date)
    pred_month, pred_day = parse_month_day(pred_date)
    if key_month is None:
        return key_day == pred_day
    return key_month == pred_month and key_day == pred_day


def match_items(predicted, keys):
    candidates = []
    for i, pred in enumerate(predicted):
        for j, key in enumerate(keys):
            score = task_similarity(pred["task"], key["task"])
            if score >= MATCH_THRESHOLD:
                candidates.append((score, i, j))
    candidates.sort(key=lambda c: -c[0])

    matched_pred, matched_key = set(), set()
    matches = []
    for score, i, j in candidates:
        if i in matched_pred or j in matched_key:
            continue
        matched_pred.add(i)
        matched_key.add(j)
        matches.append((score, i, j))

    missed = [j for j in range(len(keys)) if j not in matched_key]
    extra = [i for i in range(len(predicted)) if i not in matched_pred]
    return matches, missed, extra


def score_transcript(base, predicted, keys):
    matches, missed_idx, extra_idx = match_items(predicted, keys)

    print(f"=== {base} ===")
    for score, i, j in matches:
        print(f"  MATCH ({score:.2f}): predicted \"{predicted[i]['task']}\" <-> key \"{keys[j]['task']}\"")
    print(f"  Unmatched key items ({len(missed_idx)}):")
    for j in missed_idx:
        print(f"    - {keys[j]['task']}")
    print(f"  Unmatched predicted items ({len(extra_idx)}):")
    for i in extra_idx:
        print(f"    - {predicted[i]['task']}")

    wrong_owners = 0
    invented_owners = 0
    wrong_due_dates = 0
    invented_dates = 0
    match_details = []

    for score, i, j in matches:
        pred, key = predicted[i], keys[j]
        pred_owner, key_owner = pred.get("owner"), key.get("owner")
        pred_date, key_date = pred.get("due_date"), key.get("due_date")

        owner_correct = owners_equal(pred_owner, key_owner)
        date_correct = due_dates_equal(pred_date, key_date)

        if not owner_correct:
            wrong_owners += 1
        if key_owner is None and pred_owner is not None:
            invented_owners += 1
        if not date_correct:
            wrong_due_dates += 1
        if key_date is None and pred_date is not None:
            invented_dates += 1

        match_details.append({
            "predicted_task": pred["task"],
            "key_task": key["task"],
            "score": round(score, 3),
            "predicted_owner": pred_owner,
            "key_owner": key_owner,
            "owner_correct": owner_correct,
            "predicted_due_date": pred_date,
            "key_due_date": key_date,
            "due_date_correct": date_correct,
        })

    stats = {
        "expected": len(keys),
        "found": len(matches),
        "missed": len(missed_idx),
        "extra": len(extra_idx),
        "wrong_owners": wrong_owners,
        "invented_owners": invented_owners,
        "wrong_due_dates": wrong_due_dates,
        "invented_dates": invented_dates,
    }
    print(f"  {stats}")
    print()

    return {
        **stats,
        "matches": match_details,
        "missed_items": [keys[j]["task"] for j in missed_idx],
        "extra_items": [predicted[i]["task"] for i in extra_idx],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", default="data/outputs")
    parser.add_argument("--answers", default="data/answers")
    parser.add_argument("--provider", default="groq")
    args = parser.parse_args()

    outputs_dir = Path(args.outputs)
    answers_dir = Path(args.answers)
    suffix = f"_{args.provider}.json"

    total = {
        "expected": 0, "found": 0, "missed": 0, "extra": 0,
        "wrong_owners": 0, "invented_owners": 0,
        "wrong_due_dates": 0, "invented_dates": 0,
    }
    transcripts = {}
    skipped = []

    for output_path in sorted(outputs_dir.glob(f"*{suffix}")):
        base = output_path.name[: -len(suffix)]
        answer_path = answers_dir / f"{base}.json"
        if not answer_path.exists():
            print(f"Skipping {output_path.name}: no matching answer key at {answer_path}")
            skipped.append(base)
            continue

        predicted = json.loads(output_path.read_text())["action_items"]
        keys = json.loads(answer_path.read_text())

        result = score_transcript(base, predicted, keys)
        transcripts[base] = result
        for k in total:
            total[k] += result[k]

    summary = {
        "provider": args.provider,
        "transcripts": transcripts,
        "total": total,
        "skipped": skipped,
    }

    print(f"=== TOTAL ({args.provider}) ===")
    print(f"  {total}")

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    summary_path = results_dir / f"{args.provider}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nSaved summary to {summary_path}")


if __name__ == "__main__":
    main()
