from app.simulation.graph.base_graph import BaseGraph


class TimeTable(BaseGraph):

    default_options = {
        'content_width': 800,
        'section_height': 40,
        'margin_top': 10,
        'margin_bottom': 10,
        'margin_left': 10,
        'margin_right': 10,
        'block_font_size': 14,
        'section_font_size': 12,
        'section_name_width': 50,
    }

    def get_content_size(self):
        return (
            # width
            (
                self.options['section_name_width'] +
                self.options['content_width']
            ),
            # height
            (
                len(self.sections_names) * self.options['section_height']
            )
        )

    def draw_background(self):
        self.draw_y_axis()

    def draw_y_axis(self):
        cursor_pos = (self.options['margin_left'], self.options['margin_top'])

        for section_name in self.sections_names:

            box_sizes = (
                self.options['section_name_width'],
                self.options['section_height'],
            )

            font = self.get_font("h3")
            text_sizes = font.getsize(section_name)

            text_box_end = (
                cursor_pos[0] + box_sizes[0],
                cursor_pos[1] + box_sizes[1]
            )

            text_position = (
                cursor_pos[0] + ((box_sizes[0] - text_sizes[0]) / 2),
                cursor_pos[1] + ((box_sizes[1] - text_sizes[1]) / 2),
            )

            self.draw.rectangle((cursor_pos, text_box_end), fill="yellow")
            self.draw.text(text_position, section_name, font=font, fill="black")

            cursor_pos = (
                cursor_pos[0],
                cursor_pos[1] + self.options['section_height']
            )
            print(text_position)

    def draw_content(self):
        pass
