import torch
from transformers import AutoModelForQuestionAnswering, BertTokenizer


class PdfToKg:
    """
    Sample class to make sure things work as this is my first time trying to publish a library.
    Probably shouldn't be writing this here.
    TODO: Remove this when not needed anymore
    """

    model = AutoModelForQuestionAnswering.from_pretrained("bert-base-uncased")
    tokenizer = BertTokenizer.from_pretrained(
        "bert-large-uncased-whole-word-masking-finetuned-squad"
    )

    def answer_question(self, question: str, context: str) -> str:
        """Answers questions based on context.

        Usage example:
        ans = PdfToKg().answer_question("text", "context")

        Args:
            question (str): Question to be answered.
            context (str): Context to be used for answering the question.

        Returns:
            str: Answer to the question.

        Raises:
            None
        """
        input_ids = self.tokenizer.encode(
            question, context, truncation=True, max_length=512
        )
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids)

        sep_idx = tokens.index("[SEP]")
        token_type_ids = [0 for i in range(sep_idx + 1)] + [
            1 for i in range(sep_idx + 1, len(tokens))
        ]

        out = self.model(
            torch.tensor([input_ids]),  # The tokens representing our input text.
            token_type_ids=torch.tensor([token_type_ids]),
        )

        start_logits, end_logits = out["start_logits"], out["end_logits"]
        # Find the tokens with the highest `start` and `end` scores.
        answer_start = torch.argmax(start_logits)
        answer_end = torch.argmax(end_logits)

        ans = "".join(tokens[answer_start:answer_end])
        return ans
