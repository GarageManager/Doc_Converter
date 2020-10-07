class PDFObject:
    def __init__(self, number, content):
        self.number = number
        self.content = content
        self.offset = 0

    def __len__(self):
        length = 18 + len(self.content.encode("utf-8"))

        n = self.number
        while n > 0:
            length += 1
            n //= 10

        return length

    def __str__(self):
        return f'{self.number} 0 obj\r\n' \
               f'{self.content}\r\n'\
               f'endobj\r\n'
