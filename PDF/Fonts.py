from Tools.Enums import Fonts
from Tools.Functions import rgb_to_non_linear


def set_fonts(family_default_name, family_bold_name):
    return {
        Fonts.CodeBlock: CodeBlockFont(family_default_name),
        Fonts.CodeBlockDefault: CodeBlockFontDefault(family_default_name),
        Fonts.CodeBlockName: CodeBlockNameFont(family_default_name),
        Fonts.Filename: FileNameFont(family_bold_name),
        Fonts.Title: TitleFont(family_bold_name),
        Fonts.Item: ItemFont(family_default_name),
        Fonts.ObjectName: ObjectNameFont(family_bold_name),
        Fonts.Default: DefaultFont(family_default_name),
        Fonts.DefaultBold: DefaultBoldFont(family_bold_name),
        Fonts.XMLTitle: XMLTitleFont(family_bold_name),
        Fonts.Subtitle: SubTitleFont(family_bold_name),
        Fonts.XMLLink: XMLLinkFont(family_bold_name),
        Fonts.XMLName: XMLNameFont(family_default_name),
        Fonts.PageNumber: PageNumberFont(family_default_name)
    }


class Font:
    def __init__(self, size, family, is_bold, color=(227, 227, 227)):
        self.size = size
        self.bottom_padding = int(self.size * 0.3)
        self.line_height = self.size + self.bottom_padding
        self.name = (family+'-Bold').lower() if is_bold else family.lower()
        self.bold = is_bold
        self.char_width_cache = {}
        self.color = rgb_to_non_linear(*color)

    def __eq__(self, other):
        return (self.bold == other.bold and self.color == other.color
                and self.size == other.size)


class CodeBlockFontDefault(Font):
    def __init__(self, family):
        super().__init__(16, family, False)


class CodeBlockNameFont(Font):
    def __init__(self, family):
        super().__init__(16, family, False,  color=(1, 205, 255))


class CodeBlockFont(Font):
    def __init__(self, family):
        super().__init__(16, family, False, color=(86, 156, 214))


class FileNameFont(Font):
    def __init__(self, family):
        super().__init__(30, family, True)


class ObjectNameFont(Font):
    def __init__(self, family):
        super().__init__(26, family, True)


class TitleFont(Font):
    def __init__(self, family):
        super().__init__(22, family, True)


class SubTitleFont(Font):
    def __init__(self, family):
        super().__init__(18, family, True)


class ItemFont(Font):
    def __init__(self, family):
        super().__init__(14, family, False, color=(77, 178, 255))


class DefaultFont(Font):
    def __init__(self, family):
        super().__init__(14, family, False)


class DefaultBoldFont(Font):
    def __init__(self, family):
        super().__init__(14, family, True)


class XMLTitleFont(Font):
    def __init__(self, family):
        super().__init__(18, family, True)


class XMLLinkFont(Font):
    def __init__(self, family):
        super().__init__(14, family, False, color=(77, 178, 255))


class XMLNameFont(Font):
    def __init__(self, family):
        super().__init__(14, family, False,  color=(1, 205, 255))


class PageNumberFont(Font):
    def __init__(self, family):
        super().__init__(12, family, False)
