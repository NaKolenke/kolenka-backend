from peewee import *

database = SqliteDatabase('turkey.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class KoAchievementList(BaseModel):
    filename = CharField()
    id = IntegerField()
    link = CharField()
    name = CharField()

    class Meta:
        table_name = 'ko_achievement_list'
        primary_key = False

class KoAchievementUser(BaseModel):
    achievement = IntegerField(column_name='achievement_id')
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'ko_achievement_user'
        primary_key = False

class TuAdminban(BaseModel):
    banactive = IntegerField()
    bancomment = CharField(null=True)
    bandate = DateTimeField()
    banline = DateTimeField(null=True)
    banunlim = IntegerField()
    banwarn = IntegerField()
    id = IntegerField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_adminban'
        primary_key = False

class TuAdminips(BaseModel):
    banactive = IntegerField()
    bancomment = CharField(null=True)
    bandate = DateTimeField()
    banline = DateTimeField(null=True)
    banunlim = IntegerField()
    id = IntegerField()
    ip1 = IntegerField(null=True)
    ip2 = IntegerField(null=True)

    class Meta:
        table_name = 'tu_adminips'
        primary_key = False

class TuAdminset(BaseModel):
    adminset = IntegerField(column_name='adminset_id')
    adminset_key = CharField()
    adminset_val = TextField()

    class Meta:
        table_name = 'tu_adminset'
        primary_key = False

class TuBanner(BaseModel):
    banner_add_date = DateTimeField(null=True)
    banner_edit_date = DateTimeField(null=True)
    banner_end_date = DateField(null=True)
    banner_html = UnknownField()  # longtext
    banner = IntegerField(column_name='banner_id')
    banner_image = CharField(null=True)
    banner_is_active = IntegerField()
    banner_lang = CharField(null=True)
    banner_name = CharField(null=True)
    banner_start_date = DateField(null=True)
    banner_type = IntegerField()
    banner_url = CharField(null=True)
    bannes_is_show = IntegerField()

    class Meta:
        table_name = 'tu_banner'
        primary_key = False

class TuBannerPages(BaseModel):
    place = IntegerField(column_name='place_id')
    place_name = CharField(null=True)
    place_url = CharField(null=True)

    class Meta:
        table_name = 'tu_banner_pages'
        primary_key = False

class TuBannerPlaceHolders(BaseModel):
    banner = IntegerField(column_name='banner_id')
    page = IntegerField(column_name='page_id')
    place_type = IntegerField()

    class Meta:
        table_name = 'tu_banner_place_holders'
        primary_key = False

class TuBannerStats(BaseModel):
    banner = IntegerField(column_name='banner_id')
    click_count = IntegerField()
    stat_date = DateField()
    stats = IntegerField(column_name='stats_id')
    view_count = IntegerField()

    class Meta:
        table_name = 'tu_banner_stats'
        primary_key = False

class TuBlog(BaseModel):
    blog_avatar = CharField(null=True)
    blog_count_topic = IntegerField()
    blog_count_user = IntegerField()
    blog_count_vote = IntegerField()
    blog_date_add = DateTimeField()
    blog_date_edit = DateTimeField(null=True)
    blog_description = TextField()
    blog = IntegerField(column_name='blog_id')
    blog_limit_rating_topic = UnknownField()  # float(9,3)
    blog_order = IntegerField(null=True)
    blog_rating = UnknownField()  # float(9,3)
    blog_title = CharField()
    blog_type = CharField(null=True)
    blog_url = CharField(null=True)
    user_owner = IntegerField(column_name='user_owner_id')

    class Meta:
        table_name = 'tu_blog'
        primary_key = False

class TuBlogType(BaseModel):
    acl_comment = IntegerField(null=True)
    acl_read = IntegerField(null=True)
    acl_write = IntegerField(null=True)
    active = IntegerField(null=True)
    allow_add = IntegerField(null=True)
    allow_list = IntegerField(null=True)
    candelete = IntegerField(null=True)
    content_type = CharField(null=True)
    id = IntegerField()
    index_ignore = IntegerField(null=True)
    membership = IntegerField(null=True)
    min_rate_add = UnknownField(null=True)  # float
    min_rate_comment = UnknownField(null=True)  # float
    min_rate_list = UnknownField(null=True)  # float
    min_rate_read = UnknownField(null=True)  # float
    min_rate_write = UnknownField(null=True)  # float
    norder = IntegerField(null=True)
    type_code = CharField()
    type_description = CharField(null=True)
    type_name = CharField()

    class Meta:
        table_name = 'tu_blog_type'
        primary_key = False

class TuBlogTypeContent(BaseModel):
    blog_type = IntegerField(column_name='blog_type_id')
    content = IntegerField(column_name='content_id')

    class Meta:
        table_name = 'tu_blog_type_content'
        primary_key = False

class TuBlogUser(BaseModel):
    blog = IntegerField(column_name='blog_id')
    user = IntegerField(column_name='user_id')
    user_role = IntegerField(null=True)

    class Meta:
        table_name = 'tu_blog_user'
        primary_key = False

class TuCategory(BaseModel):
    category_active = IntegerField()
    category_avatar = CharField(null=True)
    category = IntegerField(column_name='category_id')
    category_sort = IntegerField()
    category_title = CharField()
    category_url = CharField()

    class Meta:
        table_name = 'tu_category'
        primary_key = False

class TuCategoryRel(BaseModel):
    blog = IntegerField(column_name='blog_id')
    category = IntegerField(column_name='category_id')
    rel = IntegerField(column_name='rel_id')

    class Meta:
        table_name = 'tu_category_rel'
        primary_key = False

class TuComment(BaseModel):
    comment_count_favourite = IntegerField()
    comment_count_vote = IntegerField()
    comment_date = DateTimeField()
    comment_date_edit = DateTimeField(null=True)
    comment_delete = IntegerField()
    comment = IntegerField(column_name='comment_id')
    comment_left = IntegerField()
    comment_level = IntegerField()
    comment_pid = IntegerField(null=True)
    comment_publish = IntegerField()
    comment_rating = UnknownField()  # float(9,3)
    comment_right = IntegerField()
    comment_text = TextField()
    comment_text_hash = CharField()
    comment_user_edit = IntegerField(null=True)
    comment_user_ip = CharField()
    target = IntegerField(column_name='target_id', null=True)
    target_parent = IntegerField(column_name='target_parent_id')
    target_type = CharField(null=True)
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_comment'
        primary_key = False

class TuCommentOnline(BaseModel):
    comment = IntegerField(column_name='comment_id')
    comment_online = IntegerField(column_name='comment_online_id')
    target = IntegerField(column_name='target_id', null=True)
    target_parent = IntegerField(column_name='target_parent_id')
    target_type = CharField(null=True)

    class Meta:
        table_name = 'tu_comment_online'
        primary_key = False

class TuCommentToken(BaseModel):
    token_data = CharField()
    token_data_secret = CharField()
    token_expire = IntegerField(null=True)
    token = IntegerField(column_name='token_id')
    token_image = CharField(null=True)
    token_provider_name = CharField()
    token_provider_user = CharField(column_name='token_provider_user_id')
    token_user_email = CharField(null=True)
    token_user_login = CharField(null=True)

    class Meta:
        table_name = 'tu_comment_token'
        primary_key = False

class TuContent(BaseModel):
    content_access = IntegerField()
    content_active = IntegerField()
    content_cancreate = IntegerField()
    content_candelete = IntegerField()
    content_config = TextField(null=True)
    content = IntegerField(column_name='content_id')
    content_sort = IntegerField()
    content_title = CharField()
    content_title_decl = CharField()
    content_url = CharField()

    class Meta:
        table_name = 'tu_content'
        primary_key = False

class TuContentField(BaseModel):
    content = IntegerField(column_name='content_id')
    field_description = CharField()
    field = IntegerField(column_name='field_id')
    field_name = CharField()
    field_options = TextField(null=True)
    field_postfix = TextField(null=True)
    field_required = IntegerField()
    field_sort = IntegerField()
    field_type = CharField()

    class Meta:
        table_name = 'tu_content_field'
        primary_key = False

class TuContentValues(BaseModel):
    field = IntegerField(column_name='field_id')
    field_type = CharField()
    id = IntegerField()
    target = IntegerField(column_name='target_id', null=True)
    target_type = CharField()
    value = TextField()
    value_source = TextField()
    value_type = TextField(null=True)
    value_varchar = CharField(null=True)

    class Meta:
        table_name = 'tu_content_values'
        primary_key = False

class TuDeletedTopic(BaseModel):
    deleted_time = DateTimeField()
    topic = IntegerField(column_name='topic_id')
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_deleted_topic'
        primary_key = False

class TuFavourite(BaseModel):
    tags = CharField()
    target = IntegerField(column_name='target_id', null=True)
    target_publish = IntegerField(null=True)
    target_type = CharField(null=True)
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_favourite'
        primary_key = False

class TuFavouriteTag(BaseModel):
    is_user = IntegerField()
    target = IntegerField(column_name='target_id')
    target_type = CharField(null=True)
    text = CharField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_favourite_tag'
        primary_key = False

class TuFriend(BaseModel):
    status_from = IntegerField()
    status_to = IntegerField()
    user_from = IntegerField()
    user_to = IntegerField()

    class Meta:
        table_name = 'tu_friend'
        primary_key = False

class TuGeoCity(BaseModel):
    country = IntegerField(column_name='country_id')
    id = IntegerField()
    name_en = CharField()
    name_ru = CharField()
    region = IntegerField(column_name='region_id')
    sort = IntegerField()

    class Meta:
        table_name = 'tu_geo_city'
        primary_key = False

class TuGeoCountry(BaseModel):
    code = CharField()
    id = IntegerField()
    name_en = CharField()
    name_ru = CharField()
    sort = IntegerField()

    class Meta:
        table_name = 'tu_geo_country'
        primary_key = False

class TuGeoRegion(BaseModel):
    country = IntegerField(column_name='country_id')
    id = IntegerField()
    name_en = CharField()
    name_ru = CharField()
    sort = IntegerField()

    class Meta:
        table_name = 'tu_geo_region'
        primary_key = False

class TuGeoTarget(BaseModel):
    city = IntegerField(column_name='city_id', null=True)
    country = IntegerField(column_name='country_id', null=True)
    geo = IntegerField(column_name='geo_id')
    geo_type = CharField()
    region = IntegerField(column_name='region_id', null=True)
    target = IntegerField(column_name='target_id')
    target_type = CharField()

    class Meta:
        table_name = 'tu_geo_target'
        primary_key = False

class TuInvite(BaseModel):
    invite_code = CharField()
    invite_date_add = DateTimeField()
    invite_date_used = DateTimeField(null=True)
    invite = IntegerField(column_name='invite_id')
    invite_used = IntegerField()
    user_from = IntegerField(column_name='user_from_id')
    user_to = IntegerField(column_name='user_to_id', null=True)

    class Meta:
        table_name = 'tu_invite'
        primary_key = False

class TuMagicrulesBlock(BaseModel):
    data = TextField()
    date_block = DateTimeField()
    date_create = DateTimeField()
    id = IntegerField()
    msg = CharField()
    name = CharField()
    target = CharField()
    type = IntegerField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_magicrules_block'
        primary_key = False

class TuMicroblog(BaseModel):
    mb_date_add = DateTimeField()
    mb = IntegerField(column_name='mb_id')
    mb_parent = IntegerField(column_name='mb_parent_id', null=True)
    mb_text = CharField()
    mb_user = IntegerField(column_name='mb_user_id')

    class Meta:
        table_name = 'tu_microblog'
        primary_key = False

class TuMresource(BaseModel):
    candelete = IntegerField(null=True)
    date_add = DateTimeField()
    date_del = DateTimeField(null=True)
    hash_file = CharField(null=True)
    hash_url = CharField(null=True)
    link = IntegerField()
    mresource = IntegerField(column_name='mresource_id')
    params = TextField(null=True)
    path_file = CharField(null=True)
    path_url = CharField()
    sort = IntegerField(null=True)
    storage = CharField(null=True)
    type = IntegerField()
    user = IntegerField(column_name='user_id', null=True)
    uuid = CharField()

    class Meta:
        table_name = 'tu_mresource'
        primary_key = False

class TuMresourceTarget(BaseModel):
    date_add = IntegerField()
    description = TextField(null=True)
    id = IntegerField()
    incount = IntegerField(null=True)
    mresource = IntegerField(column_name='mresource_id')
    target = IntegerField(column_name='target_id')
    target_tmp = CharField(null=True)
    target_type = CharField()

    class Meta:
        table_name = 'tu_mresource_target'
        primary_key = False

class TuNotifyTask(BaseModel):
    date_created = DateTimeField(null=True)
    notify_subject = CharField(null=True)
    notify_task = IntegerField(column_name='notify_task_id')
    notify_task_status = IntegerField(null=True)
    notify_text = TextField(null=True)
    user_login = CharField(null=True)
    user_mail = CharField(null=True)

    class Meta:
        table_name = 'tu_notify_task'
        primary_key = False

class TuPage(BaseModel):
    page_active = IntegerField()
    page_auto_br = IntegerField()
    page_date_add = DateTimeField()
    page_date_edit = DateTimeField(null=True)
    page = IntegerField(column_name='page_id')
    page_main = IntegerField()
    page_pid = IntegerField(null=True)
    page_seo_description = CharField(null=True)
    page_seo_keywords = CharField(null=True)
    page_sort = IntegerField()
    page_text = TextField()
    page_text_source = TextField()
    page_title = CharField()
    page_url = CharField()
    page_url_full = CharField()

    class Meta:
        table_name = 'tu_page'
        primary_key = False

class TuReminder(BaseModel):
    reminde_is_used = IntegerField()
    reminder_code = CharField()
    reminder_date_add = DateTimeField()
    reminder_date_expire = DateTimeField()
    reminder_date_used = DateTimeField(null=True)
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_reminder'
        primary_key = False

class TuSession(BaseModel):
    session_agent_hash = CharField(null=True)
    session_date_create = DateTimeField()
    session_date_last = DateTimeField()
    session_exit = DateTimeField(null=True)
    session_ip_create = CharField()
    session_ip_last = CharField()
    session_key = CharField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_session'
        primary_key = False

class TuStickytopicsStickyTopic(BaseModel):
    id = IntegerField()
    metadata = TextField(null=True)
    show_feed = IntegerField()
    target = IntegerField(column_name='target_id')
    target_type = TextField()
    topic = IntegerField(column_name='topic_id')
    topic_order = IntegerField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_stickytopics_sticky_topic'
        primary_key = False

class TuStorage(BaseModel):
    storage = IntegerField(column_name='storage_id')
    storage_key = CharField()
    storage_ord = IntegerField()
    storage_src = CharField(null=True)
    storage_val = TextField(null=True)

    class Meta:
        table_name = 'tu_storage'
        primary_key = False

class TuStreamEvent(BaseModel):
    date_added = UnknownField()  # timestamp
    event_type = CharField()
    id = IntegerField()
    publish = IntegerField()
    target = IntegerField(column_name='target_id')
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_stream_event'
        primary_key = False

class TuStreamSubscribe(BaseModel):
    target_user = IntegerField(column_name='target_user_id')
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_stream_subscribe'
        primary_key = False

class TuStreamUserType(BaseModel):
    event_type = CharField(null=True)
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_stream_user_type'
        primary_key = False

class TuSubscribe(BaseModel):
    date_add = DateTimeField()
    date_remove = DateTimeField(null=True)
    id = IntegerField()
    ip = CharField()
    key = CharField(null=True)
    mail = CharField()
    status = IntegerField()
    target = IntegerField(column_name='target_id', null=True)
    target_type = CharField()
    user = IntegerField(column_name='user_id', null=True)

    class Meta:
        table_name = 'tu_subscribe'
        primary_key = False

class TuTalk(BaseModel):
    talk_comment_id_last = IntegerField(null=True)
    talk_count_comment = IntegerField()
    talk_date = DateTimeField()
    talk_date_last = DateTimeField()
    talk = IntegerField(column_name='talk_id')
    talk_text = UnknownField()  # mediumtext
    talk_title = CharField()
    talk_user_id_last = IntegerField()
    talk_user_ip = CharField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_talk'
        primary_key = False

class TuTalkBlacklist(BaseModel):
    user = IntegerField(column_name='user_id')
    user_target = IntegerField(column_name='user_target_id')

    class Meta:
        table_name = 'tu_talk_blacklist'
        primary_key = False

class TuTalkUser(BaseModel):
    comment_count_new = IntegerField()
    comment_id_last = IntegerField()
    date_last = DateTimeField(null=True)
    talk = IntegerField(column_name='talk_id')
    talk_user_active = IntegerField(null=True)
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_talk_user'
        primary_key = False

class TuTopic(BaseModel):
    blog = IntegerField(column_name='blog_id')
    topic_count_comment = IntegerField()
    topic_count_favourite = IntegerField()
    topic_count_read = IntegerField()
    topic_count_vote = IntegerField()
    topic_count_vote_abstain = IntegerField()
    topic_count_vote_down = IntegerField()
    topic_count_vote_up = IntegerField()
    topic_cut_text = CharField(null=True)
    topic_date_add = DateTimeField()
    topic_date_edit = DateTimeField(null=True)
    topic_date_show = DateTimeField(null=True)
    topic_forbid_comment = IntegerField()
    topic = IntegerField(column_name='topic_id')
    topic_index_ignore = IntegerField(null=True)
    topic_order = IntegerField(null=True)
    topic_publish = IntegerField()
    topic_publish_draft = IntegerField()
    topic_publish_index = IntegerField()
    topic_rating = UnknownField()  # float(9,3)
    topic_tags = CharField()
    topic_text_hash = CharField()
    topic_title = CharField()
    topic_type = CharField(null=True)
    topic_url = CharField(null=True)
    topic_user_ip = CharField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_topic'
        primary_key = False

class TuTopicContent(BaseModel):
    topic_extra = TextField()
    topic = IntegerField(column_name='topic_id')
    topic_text = UnknownField()  # longtext
    topic_text_short = TextField()
    topic_text_source = UnknownField()  # longtext

    class Meta:
        table_name = 'tu_topic_content'
        primary_key = False

class TuTopicPhoto(BaseModel):
    date_add = UnknownField(null=True)  # timestamp
    description = TextField(null=True)
    id = IntegerField()
    path = CharField()
    target_tmp = CharField(null=True)
    topic = IntegerField(column_name='topic_id', null=True)

    class Meta:
        table_name = 'tu_topic_photo'
        primary_key = False

class TuTopicQuestionVote(BaseModel):
    answer = IntegerField()
    topic = IntegerField(column_name='topic_id')
    user_voter = IntegerField(column_name='user_voter_id')

    class Meta:
        table_name = 'tu_topic_question_vote'
        primary_key = False

class TuTopicRead(BaseModel):
    comment_count_last = IntegerField()
    comment_id_last = IntegerField()
    date_read = DateTimeField()
    topic = IntegerField(column_name='topic_id')
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_topic_read'
        primary_key = False

class TuTopicTag(BaseModel):
    blog = IntegerField(column_name='blog_id')
    topic = IntegerField(column_name='topic_id')
    topic_tag = IntegerField(column_name='topic_tag_id')
    topic_tag_text = CharField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_topic_tag'
        primary_key = False

class TuTrack(BaseModel):
    date_add = DateTimeField()
    date_remove = DateTimeField(null=True)
    id = IntegerField()
    ip = CharField()
    key = CharField(null=True)
    status = IntegerField()
    target = IntegerField(column_name='target_id', null=True)
    target_type = CharField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_track'
        primary_key = False

class TuUser(BaseModel):
    user_activate = IntegerField()
    user_activate_key = CharField(null=True)
    user_count_vote = IntegerField()
    user_date_activate = DateTimeField(null=True)
    user_date_comment_last = DateTimeField(null=True)
    user_date_register = DateTimeField()
    user = IntegerField(column_name='user_id')
    user_ip_register = CharField()
    user_last_session = CharField(null=True)
    user_login = CharField()
    user_mail = CharField()
    user_password = CharField()
    user_profile_about = TextField(null=True)
    user_profile_avatar = CharField(null=True)
    user_profile_birthday = DateField(null=True)
    user_profile_city = CharField(null=True)
    user_profile_country = CharField(null=True)
    user_profile_date = DateTimeField(null=True)
    user_profile_foto = CharField(null=True)
    user_profile_name = CharField(null=True)
    user_profile_region = CharField(null=True)
    user_profile_sex = TextField()
    user_rating = UnknownField()  # float(9,3)
    user_role = IntegerField()
    user_settings_notice_new_comment = IntegerField()
    user_settings_notice_new_friend = IntegerField()
    user_settings_notice_new_talk = IntegerField()
    user_settings_notice_new_topic = IntegerField()
    user_settings_notice_reply_comment = IntegerField()
    user_settings_timezone = CharField(null=True)
    user_skill = UnknownField()  # float(9,3)

    class Meta:
        table_name = 'tu_user'
        primary_key = False

class TuUserAdministrator(BaseModel):
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_user_administrator'
        primary_key = False

class TuUserChangemail(BaseModel):
    code_from = CharField()
    code_to = CharField()
    confirm_from = IntegerField()
    confirm_to = IntegerField()
    date_add = DateTimeField()
    date_expired = DateTimeField()
    date_used = DateTimeField(null=True)
    id = IntegerField()
    mail_from = CharField()
    mail_to = CharField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_user_changemail'
        primary_key = False

class TuUserField(BaseModel):
    id = IntegerField()
    name = CharField()
    pattern = CharField(null=True)
    title = CharField()
    type = CharField()

    class Meta:
        table_name = 'tu_user_field'
        primary_key = False

class TuUserFieldValue(BaseModel):
    field = IntegerField(column_name='field_id', null=True)
    user = IntegerField(column_name='user_id')
    value = CharField(null=True)

    class Meta:
        table_name = 'tu_user_field_value'
        primary_key = False

class TuUserNote(BaseModel):
    date_add = DateTimeField()
    id = IntegerField()
    target_user = IntegerField(column_name='target_user_id')
    text = TextField()
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_user_note'
        primary_key = False

class TuUserfeedSubscribe(BaseModel):
    subscribe_type = IntegerField()
    target = IntegerField(column_name='target_id')
    user = IntegerField(column_name='user_id')

    class Meta:
        table_name = 'tu_userfeed_subscribe'
        primary_key = False

class TuVote(BaseModel):
    target = IntegerField(column_name='target_id')
    target_type = CharField()
    user_voter = IntegerField(column_name='user_voter_id')
    vote_date = DateTimeField()
    vote_direction = IntegerField(null=True)
    vote_ip = CharField()
    vote_value = UnknownField()  # float(9,3)

    class Meta:
        table_name = 'tu_vote'
        primary_key = False

class TuWall(BaseModel):
    count_reply = IntegerField()
    date_add = DateTimeField()
    id = IntegerField()
    ip = CharField()
    last_reply = CharField()
    pid = IntegerField(null=True)
    text = TextField()
    user = IntegerField(column_name='user_id')
    wall_user = IntegerField(column_name='wall_user_id')

    class Meta:
        table_name = 'tu_wall'
        primary_key = False

