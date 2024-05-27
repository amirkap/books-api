# Description: This file contains utility functions for validating input data.
from flask_restful import reqparse


def get_post_parser():
    """Return a RequestParser object for POST requests."""
    post_parser = reqparse.RequestParser(bundle_errors=True)
    post_parser.add_argument('title', type=str, required=True, help='Title cannot be blank!')
    post_parser.add_argument('ISBN', type=str, required=True, help='ISBN cannot be blank!')
    post_parser.add_argument('genre', type=str,
                             choices=(
                             'Fiction', 'Children', 'Biography', 'Science', 'Science Fiction', 'Fantasy', 'Other'),
                             required=True,
                             help='Genre must be one of Fiction, Children, Biography, Science, Science Fiction, Fantasy, or Other')
    return post_parser


def get_put_parser():
    """Return a RequestParser object for PUT requests."""
    put_parser = get_post_parser().copy()
    put_parser.add_argument('authors', type=str, required=True, help="Authors cannot be blank!")
    put_parser.add_argument('publisher', type=str, required=True, help="Publisher cannot be blank!")
    put_parser.add_argument('publishedDate', type=str, required=True, help="Published Date cannot be blank!")

    return put_parser
