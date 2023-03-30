from django.http import HttpResponse


def get_txt(value):
                filename = 'shopping_list.txt'
                shopping_list = (
                    'Список покупок:\n\n'
                )
                for ing in value:
                    shopping_list += (
                        f'{ing["ingredient__name"]}: {ing["amount"]}'
                        f' {ing["ingredient__measurement_unit"]}\n'
                    )
                response = HttpResponse(
                    shopping_list, content_type='text.txt; charset=utf-8'
                )
                response['Content-Disposition'] = f'attachment; filename={filename}'
                return response