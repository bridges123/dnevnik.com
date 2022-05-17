from django import template

register = template.Library()


@register.filter
def round_num(value):
    if value:
        nums = str(value).split('.')
        if len(nums) > 1:
            if int(nums[1][0]) >= 5:
                return int(nums[0]) + 1
        return int(nums[0])
    return ''
