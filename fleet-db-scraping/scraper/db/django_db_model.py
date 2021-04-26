#!/usr/bin/env python3
# coding=utf-8

"""
    Django DB model for Fleet Web Scraper.

    Created:  Dmitrii Gusev, 26.04.2021
    Modified:

"""

# todo: https://habr.com/ru/company/domclick/blog/552930/

from django.db import models


class DBShip(models.Model):
    class Meta:
        db_table = 'ships'

    imo_number = models.TextField(unique=True)
    reg_number = models.TextField()
    flag = models.TextField()
    main_name = models.TextField()
    secondary_name = models.TextField()
    home_port = models.TextField()
    call_sign = models.TextField()


# class Topic(models.Model):
#     class Meta:
#         db_table = 'topic'
#
#     title = models.TextField()
#     image = models.ForeignKey(Image, on_delete=models.DO_NOTHING)
#     users = models.ManyToManyField('User', through='TopicUser')
#
#
# class Question(models.Model):
#     class Meta:
#         db_table = 'question'
#
#     text = models.TextField()
#     topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING, related_name='questions')
#
#
# class TopicUser(models.Model):
#     class Meta:
#         db_table = 'topic_user'
#
#     topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING)
#     user = models.ForeignKey('User', on_delete=models.DO_NOTHING)
#     role = models.TextField(max_length=64)
#
#
# class User(models.Model):
#     class Meta:
#         db_table = 'user'
#
#     name = models.TextField()