import re

class PaperParser:
    def __init__(self):
        self.section_regex = re.compile('#0033cc"><b>([^<]+)</b>')
        self.title_regex = re.compile('0in"><b>([^<]+)</b>')
        self.author_regex = re.compile('<em>(.+)</em>')

        self.index = 0

        self.dict = {}
    
    def strip(self, string):
        middle = string.decode('utf8')
        middle = middle.strip()
        middle = middle.replace(u'\xa0', '')

        return middle.encode('utf8')
    
    def parse(self, input, output):
        pass

    def parse_string(self, string):
        lines = string.split('\r\n')

        section = None
        title = None
        author = None

        for line in lines:
            value = self.is_section(line)
            if value:
                if title or author:
                    raise Exception('parse', 'Got section but title or author exists', value)

                section = value
                continue

            value = self.is_title(line)
            if value:
                if not section:
                    raise Exception('parse', 'No Section when title found', value)

                if author:
                    raise Exception('parse', 'Got title but Author exists', value)

                title = value
                continue

            value = self.is_author(line)
            if value:
                if not section or not title:
                    raise Exception('parse', 'author found but no title or section', value)
                    
                author = value

                self.dict[section].append((title, author))

                title = None
                author = None
                continue

        return self.dict

    def is_section(self, line):
        obj = self.section_regex.search(line)

        if not obj:
            return None
        else:
            section = obj.group(1)
            section = self.strip(section)

            self.dict[section] = []

            return section

    def is_title(self, line):
        obj = self.title_regex.search(line)

        if not obj:
            return None
        else:
            title = obj.group(1)

            return title

    def is_author(self, line):
        obj = self.author_regex.search(line)

        if not obj:
            return None
        else:
            author = obj.group(1)

            return author

    def get_section(self, string):
        obj = self.section_regex.search(string, self.index)

        if obj:
            print obj.start(1)
            print obj.end(1)


def replace_all(string, pattern, replacement):
    result = re.subn(pattern, replacement, string)

    return result[0]

def set_multi_line_to_one(bytes):
    pattern = '<b><br />\r\n  '
    replacement = '<b>'

    return replace_all(bytes, pattern, replacement)

def set_i_to_em(bytes):
    pattern = 'i>'
    replacement = 'em>'

    return replace_all(bytes, pattern, replacement)

def clear_br_with_newline(bytes):
    pattern = '<br />\r\n *</b>'
    replacement = '</b>'

    return replace_all(bytes, pattern, replacement)

def main(input, output, html_title):
    f = open(input, 'rb')
    out = open(output, 'wb')

    bytes = f.read()

    tmp = bytes
    tmp = set_multi_line_to_one(tmp)
    tmp = set_i_to_em(tmp)
    tmp = clear_br_with_newline(tmp)

    tmpout = open('tmp.txt', 'wb')
    tmpout.write(tmp)
    tmpout.close()

    # then use this tmp to find string...
    #
    # find sectino first
    parser = PaperParser()
    dict = parser.parse_string(tmp)

    keys = dict.keys()
    keys.sort()

    print('section count: %d' % (len(keys), ))

    # output header
    header = open('header.txt', 'rb').read()
    header = header.replace('{TITLE}', html_title)
    out.write(header)

    # output paper list
    for key in keys:
        section = dict[key]

        string = '<h3><span>%s</span></h3>\n<dl>\n' % (key, )
        out.write(string)

        for paper in section:
            title = paper[0]
            author = paper[1]

            string = '<dt>%s</dt>\n<dd>%s</dd>\n' % (title, author)
            out.write(string)
    
        string = '</dl>\n'
        out.write(string)
    
    # output footer
    footer = open('footer.txt', 'rb').read()
    out.write(footer)

    out.close()

if __name__ == '__main__':
    input = 'infocom2011.htm'
    output = 'infocom2011.result.htm'
    html_title = 'INFOCOM 2011 Paper List'

    main(input, output, html_title)

