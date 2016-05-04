"""
Filter to create the task parameter reports.
"""

from django import template
import pandas as pd
register = template.Library()


@register.filter
def dataframe_to_html(df, table_id="table_parameters", css_class="table table-condensed table-responsive"):
    """ Create HTML representation of a django DataFrame. """
    # create the header (columns)
    columns = df.columns
    info = ['<table id="{}" class="{}">'.format(table_id, css_class),
            '<thead>',
            '<tr>']
    for col in columns:
        info.append('<th>{}</th>'.format(col))
    info.extend(['</tr>', '</thead>', '<tbody>'])

    # create the rows
    for k in range(len(df)):
        row = ['<tr>']
        for col in columns:
            value = df[col][k]
            if pd.isnull(value):
                value = ''
            row.append('<td>{}</td>'.format(value))
        row.append('</tr>')
        info.append(''.join(row))

    info.extend(['</tbody>', '</table'])
    return "\n".join(info)
