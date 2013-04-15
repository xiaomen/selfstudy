# -*- coding: utf-8 -*-

def get_user_domain(user):
    if user.domain:
        return user.domain
    return user.uid

__all__ = ["get_user_domain"]
