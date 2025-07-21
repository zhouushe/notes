import base64
import sys
import zlib
from pathlib import Path

import click
import requests

BASE_URL = 'https://kroki.exia.dev'


@click.group()
def cli():
    """
    This utility can be used to encode and decode diagrams to/from the Kroki service.

    Usage examples:

    Encode a diagram file:
      python kroki_diagram_util.py encode-diagram hello.dot

    Decode an encoded diagram:
      python kroki_diagram_util.py decode-diagram 'eNpLyUwvSizIUHBXqPZIzcnJ17ULzy_KSakFAGxACMY='

    Post a diagram to the Kroki service:
      python kroki_diagram_util.py post-diagram hello.dot

    Get a diagram from the Kroki service:
      python kroki_diagram_util.py get-diagram 'eNpLyUwvSizIUHBXqPZIzcnJ17ULzy_KSakFAGxACMY='
    """
    pass


@cli.command(name='encode-diagram')
@click.argument('diagram_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file path (default: print to console)')
def encode_diagram(diagram_file, output):
    """Encode a diagram file to a URL-safe Base64 compressed string"""
    try:
        diagram_source = diagram_file.read_text(encoding='utf-8')
        encoded_diagram = base64.urlsafe_b64encode(zlib.compress(diagram_source.encode('utf-8'), level=9)).decode('ascii')

        if output:
            output.write_text(encoded_diagram, encoding='ascii')
            click.echo(f'✓ Diagram encoded and saved to {output}')
        else:
            click.echo(encoded_diagram)

        return encoded_diagram
    except Exception as error:
        click.echo(f'× Error encoding diagram: {str(error)}', err=True)
        sys.exit(1)


@cli.command(name='decode-diagram')
@click.argument('encoded_diagram')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file (default: print to console)')
def decode_diagram(encoded_diagram, output):
    """Decode a Base64 compressed string back to the original diagram"""
    try:
        decoded_diagram = zlib.decompress(base64.urlsafe_b64decode(encoded_diagram)).decode('utf-8')

        if output:
            output.write_text(decoded_diagram, encoding='utf-8')
            click.echo(f'✓ Diagram decoded and saved to {output}')
        else:
            click.echo(decoded_diagram)

        return decoded_diagram
    except Exception as error:
        click.echo(f'× Error decoding diagram: {str(error)}', err=True)
        sys.exit(1)


@cli.command(name='post-diagram')
@click.argument('diagram_file', type=click.Path(exists=True, path_type=Path))
@click.option('--diagram-type', '-t', default='graphviz', help='Diagram type (default: graphviz)')
@click.option('--output-format', '-f', default='svg', help='Output format (default: svg)')
def post_diagram(diagram_file, diagram_type='graphviz', output_format='svg'):
    """Post a diagram to the Kroki service"""
    payload = {
        'diagram_source': diagram_file.read_text(encoding='utf-8'),
        'diagram_type': diagram_type,
        'output_format': output_format
    }

    response = requests.post(url=BASE_URL, json=payload)

    if response.status_code == 200:
        click.echo(f'✓ Diagram posted to Kroki service {BASE_URL} with payload {payload}')
    else:
        click.echo(f'× Error: {response.text}', err=True)
        sys.exit(1)


@cli.command(name='get-diagram')
@click.argument('encoded_diagram')
@click.option('--diagram-type', '-t', default='graphviz', help='Diagram type (default: graphviz)')
@click.option('--output-format', '-f', default='svg', help='Output format (default: svg)')
def get_diagram(encoded_diagram, diagram_type='graphviz', output_format='svg'):
    """Get a diagram from the Kroki service"""
    url = f'{BASE_URL}/{diagram_type}/{output_format}/{encoded_diagram}'
    response = requests.get(url=url)

    if response.status_code == 200:
        click.echo(f'✓ Diagram retrieved from Kroki service {url}')
        return url

    click.echo(f'× Error: {response.text}', err=True)
    sys.exit(1)


if __name__ == '__main__':
    cli()
