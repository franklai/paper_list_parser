import logging
import re

class ParserBase:
    def output(self, content, dst):
        open(dst, 'wb').write(content.encode('utf-8'))
        
    def replace_all(self, string, pattern, replacement):
        result = re.subn(pattern, replacement, string)

        return result[0]

    def strip_tags(self, html):
        pattern = '<[^>]+>'
        return self.replace_all(html, pattern, '')

    def is_section(self, line):
        pass

    def is_title(self, line):
        pass

    def is_author(self, line):
        pass

    def output_html(self, dict):
        out = open(self.dst, 'wb')

        keys = dict.keys()
        keys.sort()

        logging.info('section count: %d' % (len(keys), ))

        # output header
        header = open('header.txt', 'rb').read().decode('utf-8')
        header = header.replace('{TITLE}', html_title)
        out.write(header.encode('utf-8'))

        # output paper list
        for key in keys:
            section = dict[key]

            string = '<h3><span>%s</span></h3>\n<dl>\n' % (key, )
            out.write(string.encode('utf-8'))

            for paper in section:
                title = paper[0]
                author = paper[1]

                string = '<dt>%s</dt>\n<dd>%s</dd>\n' % (title, author)
                out.write(string.encode('utf-8'))
        
            string = '</dl>\n'
            out.write(string.encode('utf-8'))
        
        # output footer
        footer = open('footer.txt', 'rb').read().decode('utf-8')
        out.write(footer.encode('utf-8'))

        out.close()

class ParserInfocom2014(ParserBase):
    def __init__(self, src, dst):
        self.section_regex = re.compile('color: #C00000; background: white">([^<]+)<o:p>')
        self.title_regex = re.compile('0in"><b>([^<]+)</b>')
        self.author_regex = re.compile('<em>(.+)</em>')

        self.src = src
        self.dst = dst

        self.html = open(src, 'rb').read().decode('utf-8')

    def get(self):
        # convert to easier parse format
        html = self.transform(self.html)

        # debug purpose
        self.output(html, 'tmp.txt')
#         html = open('tmp.txt', 'rb').read()

        # get section, title, author
        result = self.parse(html)

        self.output_html(result)

    def transform(self, html):
        html = self.replace_all(html, '[\r\n\t]', '')
        html = self.replace_all(html, '<p', '\n<p')

        return html

    def is_section(self, line):
        pattern = 'color: #C00000;'
        pos = line.find(pattern)

        chair = line.find('#222222')

        if pos >= 0 and chair == -1:
            return self.strip_tags(line).strip()
        return ''

    def is_title(self, line):
        pattern = '<b><i><span'
        pos = line.find(pattern)

        if pos >= 0:
            return self.strip_tags(line).strip()
        return ''

    def is_author(self, line):
        pattern = 'class="style4"'
        pos = line.find(pattern)

        if pos >= 0:
            return self.strip_tags(line).strip()
        return ''

    def parse(self, html):
        lines = html.split('\n')
        tree = {}
        section = None
        title = None
        author = None

        for line in lines:
            value = self.is_section(line)
            if value:
                if title or author:
                    raise Exception('parse', 'Got section but title or author exists', value)

                section = value
                logging.debug('section: [%s]' % (section, ))
                continue

            value = self.is_title(line)
            if value:
                if not section:
                    raise Exception('parse', 'No Section when title found', value)

                if author:
                    raise Exception('parse', 'Got title but Author exists', value)
                if title:
                    raise Exception('parse', 'Got title but title exists', value)

                title = value
                logging.debug('title: [%s]' % (title, ))
                continue

            value = self.is_author(line)
            if value:
                if not section or not title:
                    logging.info('author found but no title or section')
                    continue
#                     raise Exception('parse', 'author found but no title or section', value)
                    
                author = value
                logging.debug('author: [%s]' % (author, ))

                logging.debug('section: [%s], title [%s]' % (section, title, ))
                if section not in tree:
                    tree[section] = []
                tree[section].append((title, author))

                title = None
                author = None
                continue
            else:
                logging.info('not author, line: %s' % (line, ))

        return tree

if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG, filename='debug.log')
    logging.basicConfig(level=logging.INFO)

    input = 'src/infocom2014.htm'
    output = 'output/infocom2014.htm'
    html_title = 'INFOCOM 2014 Paper List'

    parser = ParserInfocom2014(input, output)
    parser.get()
