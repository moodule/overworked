import math
import os

# TODO estimate the (min) number of pages to create a pattern
# TODO estimate the optimal height of the book to match the ratio
# TODO you can either fold the blank pages in half or at the margin
# (the best is to fold at the margin limit so that no paper will poke out)
# the idea is to create an empty space between the parts of the pattern

folding_table_header = ''
folding_table_footer = ''
folding_table_blank_line = ''
folding_table_folded_line = ''

class Book(object):
    """Models the whole book"""
   
    def __init__(self):
        self._first_page = 1           # no unit, the total page count, equals last page number
        self._last_page = 100
        self._sheet_height = 0.2                 # taking the margin into account
        self._sheet_depth = 0.1
        self._horizontal_margin = 10             # no unit, it is the number of sheets left both before and after the pattern
        self._vertical_margin = 0.01             # in meters, the blank space left both above and under the pattern
        self._pattern = None

    def __str__(self):
        str_format = """{book_name:=<050}"""
        str_format = str_format.format(book_name='= Book ' + self._pattern.name() + ' ')
        return str_format

    def sheet_count(self):  # the actual number of pages used in the pattern
        total_sheet_count = math.ceil(float(self._last_page - self._first_page + 1) / 2.0)
        pattern_sheet_count = total_sheet_count - 2 * self._horizontal_margin
        pattern_sheet_count = max(pattern_sheet_count, 0)
        return (self._horizontal_margin, pattern_sheet_count, self._horizontal_margin)

    def sheet_height(self):
        pattern_height = self._sheet_height - 2.0 * self._vertical_margin
        pattern_height = max(0.0, pattern_height)
        return (self._vertical_margin, pattern_height, self._vertical_margin)

    def sheet_spacing(self):
        max_spacing = 2.0 * 3.1416 * self._sheet_depth
        max_spacing = max_spacing / sum(self.sheet_count())
        return (0.25 * max_spacing, 0.5 * max_spacing, max_spacing)

    def aspect_ratio(self):
        """Gives the range of possible ratios for the folded pattern.
        The ratio can be adjusted by opening the book more or less.
        The calculation is made with fixed margins."""
        pattern_sheet_count = self.sheet_count()[1]
        pattern_height = self.sheet_height()[1]
        pattern_ratio = float(pattern_sheet_count) / pattern_height
        min_ratio = self.sheet_spacing()[0] * pattern_ratio
        max_ratio = self.sheet_spacing()[2] * pattern_ratio
        opt_ratio = self.sheet_spacing()[1] * pattern_ratio
	return (min_ratio, opt_ratio, max_ratio)

    def horizontal_ranges(self):
        pattern_start_page = self._first_page + 2 * self._horizontal_margin
        pattern_end_page = pattern_start_page + 2 * self.sheet_count()[1]
        return (self._first_page, pattern_start_page, pattern_end_page, self._last_page)

    def vertical_ranges(self):
        return (0.0, self._vertical_margin, self._sheet_height - self._vertical_margin, self._sheet_height)

    def name(self):
        book_name = ''
        if self._pattern:
            book_name = self._pattern.name()
        return book_name

    def set_size(self, first_page_number, last_page_number, sheet_height, sheet_depth):
        self._first_page = first_page_number
        self._last_page = last_page_number
        self._sheet_height = sheet_height
        self._sheet_depth = sheet_depth

    def set_margins(self, page_margin, paper_margin):
        """The margins are symetrical (top = bottom, and left = right)"""
        if (self._sheet_height - (2.0 * paper_margin)) > 0.0:
            self._vertical_margin = paper_margin
        if (self._last_page - (2 * page_margin)) > 0:
            self._horizontal_margin = page_margin

    def set_pattern(self, pattern):
        self._pattern = pattern

    def calculate_margins(self):
        pass

    def save_folding_table(self, pattern_path=None):
        saving_path = os.path.join('patterns/', self.name())
        if pattern_path is not None:
            if type(pattern_path) is str and pattern_path:
                saving_path = pattern_path
        saving_path, ext = os.path.splitext(saving_path)
        ext = ext.replace('.', '')
        if not ext:
            ext = 'txt'
        saving_path += '_pattern.' + ext.lower()

        pattern_file = None
        try:
            pattern_file = open(saving_path, 'w')
        except IOError as e:
            error_message = '! Cannot open {0} !\n'
            error_message += 'Please make sure that the folder ./patterns/ exists\n'
            error_message += 'If it does check your writing permissions\n'
            error_message += 'I/O Error({1}) : {2}'
            error_message = error_message.format(saving_path, e.errno, e.strerror)
        
        blank_page_line = '{page: <04}\t{lower: <05.1}\t{upper: <05.1}\tThis page is blank !\n'
        folded_page_line = '{page: <04}\t{lower: <05.1}\t{upper: <05.1}\n'
        
        if self._pattern:
            folding_table = """
{pattern_name:=<080}
The folding marks are measured from the bottom of the page.
The blank pages are meant to be fold all the way from top to bottom.
The measurements are given in cm.
{page: <04}\t{lower_mark: <05}\t{upper_mark: <05}
{filler:=<080}\n""".format(
        pattern_name='= ' + self._pattern.name() + ' ',
        page='Page',
        lower_mark='Lower',
        upper_mark='Upper',
        filler='')
        
            for i, band in enumerate(self._pattern._bands):
                is_blank_page = (band[0] == band[1])
                current_page = self._first_page + 2 * i
                lower_mark = 100.0 * self._pixel_to_sheet_coordinate(band[0])
                upper_mark = 100.0 * self._pixel_to_sheet_coordinate(band[1])
                if is_blank_page:
                    lower_mark = 0.0
                    upper_mark = 100.0 * self._sheet_height
                    folding_table += blank_page_line.format(
                            page=current_page,
                            lower=lower_mark,
                            upper=upper_mark)
                else:
                    folding_table += folded_page_line.format(
                            page=current_page,
                            lower=lower_mark,
                            upper=upper_mark)

        if pattern_file:
            pattern_file.write(folding_table)
            pattern_file.close()
            print 'Your pattern has been saved to {file_path}.'.format(file_path=saving_path)

    def fold(self):
        pass

    def _pixel_to_sheet_coordinate(self, pixel_y):
        pixel_ratio = self._pattern.vertical_coordinate_ratio(pixel_y, from_top=False, raw=False)
        coordinate = self._vertical_margin + (pixel_ratio * self.sheet_height()[1])
        return coordinate
