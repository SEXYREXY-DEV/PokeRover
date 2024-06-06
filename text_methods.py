class TextWrapper:
    @staticmethod
    def wrap_text(text, max_width, break_every=3):
        words = text.split(',')
        lines = []
        current_line = ""
        current_length = 0
        comma_count = 0
        for word in words:
            word = word.strip()
            if current_length + len(word) <= max_width:
                if current_line:  # Add space if not first word in line
                    current_line += ", "  # Add comma and space
                    current_length += 2
                current_line += word
                current_length += len(word)
                if word:  # If word is not empty
                    comma_count += 1
                    if comma_count % break_every == 0:  # Break line every break_every commas
                        lines.append(current_line)
                        current_line = ""
                        current_length = 0
            else:
                lines.append(current_line)
                current_line = word
                current_length = len(word)
        if current_line:  # Append any remaining words
            lines.append(current_line)
        return "\n".join(lines)
