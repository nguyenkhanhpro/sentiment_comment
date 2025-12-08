#!/usr/bin/env python3
import re
from typing import List, Optional
import csv
from pathlib import Path

import py_vncorenlp as vlp  # type: ignore
from transformers import pipeline  # type: ignore
import unicodedata
import regex  # type: ignore
import json

# Thêm import torch để kiểm tra CUDA
try:
    import torch  # type: ignore
except Exception:
    torch = None


class TextProcessor:
    def __init__(self, model_path: str, use_hf: bool = True, hf_device: Optional[int] = None):
        self.model = vlp.VnCoreNLP(annotators=["wseg"], save_dir=model_path)
        self.EMOJI_ZWJ_PATTERN = regex.compile(r'[\p{Emoji}\p{Extended_Pictographic}\u200D\uFE0F]+')
        self.NON_ALNUM_SPACE_PATTERN = regex.compile(r'[^\p{L}\p{N}\s]+')

        # quyết định device cho HF pipeline
        # hf_device nếu truyền (ví dụ 0) sẽ được ưu tiên
        device_to_use = -1  # default: CPU
        if hf_device is not None:
            device_to_use = int(hf_device)
        else:
            if torch is not None and torch.cuda.is_available():
                device_to_use = 0  # GPU 0
        # lưu device để debug
        self.hf_device = device_to_use

        self.corrector = None
        if use_hf:
            try:
                # truyền device để pipeline chạy trên GPU khi device>=0
                self.corrector = pipeline("text2text-generation",
                                          model="bmd1905/vietnamese-correction-v2",
                                          device=self.hf_device)
                print(f"[INFO] HF pipeline khởi tạo, device = {self.hf_device} "
                      f"({'cuda' if self.hf_device >= 0 else 'cpu'})")
            except Exception as e:
                print(f"[WARN] Không thể khởi tạo HF pipeline: {e}")
                self.corrector = None

        try:
            mapping_file = Path(__file__).parent / "mapping.json"
            self.abbrev_map = json.loads(mapping_file.read_text(encoding="utf-8"))
            self.re_abbrev = regex.compile(
                r"\b(" + "|".join(map(regex.escape, self.abbrev_map.keys())) + r")\b",
                flags=regex.UNICODE
            )
        except Exception as e:
            print(f"[WARN] Không thể nạp mapping.json: {e}")
            self.abbrev_map = {}
            self.re_abbrev = regex.compile(r"(?!x)x")

    def remove_repeat(self, text: str) -> str:
        REPEAT = re.compile(r"([^\W\d_])\1{1,}", flags=re.UNICODE)
        return REPEAT.sub(r"\1", text)

    def clean_text_strict(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        s = unicodedata.normalize("NFC", text)
        s = self.EMOJI_ZWJ_PATTERN.sub("", s)
        s = self.NON_ALNUM_SPACE_PATTERN.sub("", s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def text_correction(self, s: str, max_length: int = 512) -> str:
        if self.corrector is None:
            return s
        try:
            out = self.corrector([s], max_length=max_length)
            if out and isinstance(out[0], dict):
                return out[0].get("generated_text", s)
            return s
        except Exception:
            return s

    def normalize_abbreviation(self, text: str) -> str:
        def _repl(m: regex.Match) -> str:
            key = m.group(1)
            return self.abbrev_map.get(key, key)
        return self.re_abbrev.sub(_repl, text)

    def tokenize_text(self, text: str, per_sentence: bool = False) -> List:
        segmented_sentences = self.model.word_segment(text)
        sentences_tokens = [s.split() for s in segmented_sentences]
        if per_sentence:
            return sentences_tokens
        flat_tokens: List[str] = []
        for sent in sentences_tokens:
            flat_tokens.extend(sent)
        return flat_tokens

    def lower_text(self, text: str) -> str:
        return text.lower()

    def check_link_spam(self, text: str) -> bool:
        url_pattern = re.compile(r"""(?xi)\b((?:https?://|www\.)[^\s<>"']+)""")
        return bool(url_pattern.search(text))

    def close(self):
        try:
            self.model.close()
        except Exception:
            pass


def process_text_workflow(processor: TextProcessor, text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None

    s = processor.lower_text(s)
    if processor.check_link_spam(s):
        return None

    s = processor.clean_text_strict(s)
    s = processor.remove_repeat(s)
    if not s.strip():
        return None

    s = processor.normalize_abbreviation(s)
    s = processor.text_correction(s)
    s = s.strip()
    if not s:
        return None

    return s


if __name__ == "__main__":
    processor = TextProcessor(model_path=r"C:/Users/Admin/AppData/Local/vncorenlp", use_hf=True)

    base_dir = Path(__file__).parent
    input_csv = base_dir / "data/comments_text_labeled.csv"
    output_csv = base_dir / "data/comments_text_labeled_output.csv"

    if not input_csv.exists():
        raise FileNotFoundError(f"Không tìm thấy file CSV: {input_csv}")

    BATCH_SIZE = 1000
    written = 0

    with input_csv.open("r", encoding="utf-8", newline="") as f_in, \
         output_csv.open("w", encoding="utf-8", newline="") as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)

        header = next(reader, None)
        if header is not None:
            writer.writerow(header)

        buffer: List[List[str]] = []

        for row in reader:
            if not row or len(row) == 0:
                continue

            text_orig = row[0]
            processed = process_text_workflow(processor, text_orig)
            if processed is None:
                continue

            row_out = [processed] + row[1:]
            buffer.append(row_out)

            if len(buffer) >= BATCH_SIZE:
                writer.writerows(buffer)
                written += len(buffer)
                buffer.clear()

        # flush phần còn lại
        if buffer:
            writer.writerows(buffer)
            written += len(buffer)

    print(f"Đã xử lý theo streaming với batch {BATCH_SIZE}. Số dòng ghi ra: {written} -> {output_csv}")

    processor.close()