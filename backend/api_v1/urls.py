from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from backend.api_v1.jwt_auth import CustomTokenObtainPairView
from backend.users import curator_views
from backend.courses.views.admin_views import (
    TagListCreate,
    TagDetail,
    CourseListCreate,
    CourseDetail,
    MaterialListCreate,
    MaterialDetail,
    TaskListCreate,
    TaskDetail,
    QuestionListCreate,
    QuestionDetail,
    AnswerListCreate,
    AnswerDetail,
    MaterialPassingViewSet,
    TestPassingViewSet,
    TestPassingDetail,
    QuestionFromFileCreation,
    MaterialCopy,
    MaterialFullCopy,
    MaterialSingleCopy,
    TaskCopy
)
from backend.courses.views.client_views import (
    CourseClientViewSet,
    CourseClientAllViewSet,
    TagClientViewSet,
    MaterialClientViewSet,
    TaskClientViewSet,
    QuestionClientViewSet,
    AnswerClientViewSet,
    MaterialPassingListCreate,
    MaterialPassingListAll,
    MaterialPassingDetail,
    TestPassingClientListCreate,
    EndTestPassingClientView,
    BookmarkListCreate,
    BookmarkDetail,
    UserCourseSettingsViewSet,
    UserCourseSettingsDetail,
    CuratorUserCourseSettingsViewSet,
    ClientUserCourseSettingsViewSet
)
from backend.mess.views import (
    ChatViewSet,
    MessageViewSet,
    MassMessageView,
    GetFirebaseSettingsView,
    ChangeFirebaseSettingsViewSet,
    ChatDeleteView,
    UserMessageView,
    GetUnreadMessageCountView,
)
from backend.testing.views import (
    UserAnswerDetail,
    UserAnswerClientListCreate,
    ModeratorUserAnswerViewSet,
    ModeratorUserAnswerDetail,
    server_time,
)
from backend.users.views import (
    CompanyListCreate,
    CompanyDetail,
    MassUsersCreation,
    UserDetail,
    UserListCreate,
    UserListExamsCreate,
    UserClientView,
    CommonUserView,
    CuratorUserViewSet,
    ChangePasswordView,
    OwnChPasswordSerializer,
    UserDayActivityViewSet,
    UserActivityDetailsViewSet,
    ClientUserDayActivityViewSet,
    CourseClientADView,
    CuratorUserProgressView,
    UsersOnlineView,
    UserOnlineHistoryViewSet,
    SingleUserCreation,
    RegisterNewUser,
    UserLogErrorsViewSet
)

from backend.conference.views import GetApiKeyView, ChangeApiKeyViewSet
from backend.quickauth.views import QuickloginViews, ChangeQuickLogin
from backend.notifications.views import MessageNotificationView, MessageNotificationDetail

app_name = 'api_v1'

# JWT авторизация
jwt_patterns = ([
    path('', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
])

# API TESTING
client_testing_patterns = ([
    path('user_answer/', UserAnswerClientListCreate.as_view(), name='user_answer_list_create'),
    path('user_answer/<int:id>/', UserAnswerDetail.as_view(), name='user_answer_detail'),
])

# API USERS
company_patterns = ([
    path('company/', CompanyListCreate.as_view(), name='company_list_create'),
    path('company/<int:id>/', CompanyDetail.as_view(), name='company_detail'),
    path('mass_users/', MassUsersCreation.as_view(), name='mass_users'),
    path('single_user/', SingleUserCreation.as_view(), name='single_user'),
    path('user/', UserListCreate.as_view(), name='user_list'),
    path('user_exams/', UserListExamsCreate.as_view(), name='user_list'),
    path('user/<int:id>/', UserDetail.as_view(), name='user_detail'),
    path('user/change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('user/own_change_password/', OwnChPasswordSerializer.as_view(), name='own_change_password'),
    path('user_activity/', UserDayActivityViewSet.as_view({'get': 'list'}), name='user_activity'),
    path('user_activity_details/', UserActivityDetailsViewSet.as_view({'get': 'list'}), name='user_activity_details'),
    path('user_course/', CourseClientADView.as_view(), name='course_client_ad'),
])

# API COURSE
courses_patterns = ([
    path('tag/', TagListCreate.as_view(), name='tag_list_create'),
    path('tag/<int:id>/', TagDetail.as_view(), name='tag_detail'),
    path('course/', CourseListCreate.as_view(), name='course_list_create'),
    path('course/<int:id>/', CourseDetail.as_view(), name='course_detail'),
    path('material/', MaterialListCreate.as_view(), name='material_list_create'),
    path('material/<int:id>/', MaterialDetail.as_view(), name='material_detail'),
    path('material/copy/', MaterialCopy.as_view(), name='material_copy'),
    path('material/copy/full/', MaterialFullCopy.as_view(), name='material_copy'),
    path('material/copy/single/', MaterialSingleCopy.as_view(), name='material_single_copy'),
    path('task/', TaskListCreate.as_view(), name='task_list_create'),
    path('task/<int:id>/', TaskDetail.as_view(), name='task_detail'),
    path('task/copy/', TaskCopy.as_view(), name='task_copy'),
    path('question/', QuestionListCreate.as_view(), name='question_list_create'),
    path('question/<int:id>/', QuestionDetail.as_view(), name='question_detail'),
    path('questions_from_file/', QuestionFromFileCreation.as_view(), name='questions_from_file'),
    path('answer/', AnswerListCreate.as_view(), name='answer_list_create'),
    path('answer/<int:id>/', AnswerDetail.as_view(), name='answer_detail'),
    path('moderator_user_answers/', ModeratorUserAnswerViewSet.as_view({'get': 'list'}),
         name='moderator_user_answers_list'),
    path('moderator_user_answer/<int:id>/', ModeratorUserAnswerDetail.as_view(), name='moderator_user_answer'),
    path('material_passing/', MaterialPassingViewSet.as_view({'get': 'list'}), name='material_passing'),
    path('test_passing/', TestPassingViewSet.as_view({'get': 'list'}), name='test_passing'),
    path('test_passing/<int:id>/', TestPassingDetail.as_view(), name='test_passing_detail'),
])

# API CLIENT USERS
client_company_patterns = ([
    path('user/', UserClientView.as_view(), name='user'),
    path('activity/', ClientUserDayActivityViewSet.as_view({'get': 'list'}), name='activity'),
])

# API COMMON USERS
common_user_patterns = ([
    path('user/', CommonUserView.as_view(), name='user'),
    path('online/', UsersOnlineView.as_view(), name='users_online'),
    path('online_history/', UserOnlineHistoryViewSet.as_view({'get': 'list'}), name='users_online'),
    path('user_log_errors/', UserLogErrorsViewSet.as_view(), name='user_log_errors'),
])

# API CLIENT COURSE
client_courses_patterns = ([
    path('course/', CourseClientViewSet.as_view({'get': 'list'}), name='course_list'),
    path('course-users/', CourseClientAllViewSet.as_view({'get': 'list'}), name='course_list_users'),
    path('tag/', TagClientViewSet.as_view({'get': 'list'}), name='tag_list'),
    path('material/', MaterialClientViewSet.as_view({'get': 'list'}), name='material_list'),
    path('task/', TaskClientViewSet.as_view({'get': 'list'}), name='task_list'),
    path('question/', QuestionClientViewSet.as_view({'get': 'list'}), name='question_list'),
    path('answer/', AnswerClientViewSet.as_view({'get': 'list'}), name='answer_list'),
    path('material_passing/', MaterialPassingListCreate.as_view(), name='material_passing_create'),
    path('material_passing_all/', MaterialPassingListAll.as_view(), name='material_passing_all'),
    path('material_passing/<int:id>/', MaterialPassingDetail.as_view(), name='material_passing_detail'),
    path('test_passing/', TestPassingClientListCreate.as_view(), name='test_passing_create'),
    path('end_test_passing/<int:pk>/', EndTestPassingClientView.as_view(), name='end_test_passing'),
    path('bookmark/', BookmarkListCreate.as_view(), name='bookmark_create'),
    path('bookmark/<int:id>/', BookmarkDetail.as_view(), name='bookmark_detail'),
    path('user_course_settings/', UserCourseSettingsViewSet.as_view(), name='user_course_settings'),
    path('user_course_settings_detail/<int:id>/', UserCourseSettingsDetail.as_view(), name='user_course_settings_detail'),
    path('client_user_course_settings/', ClientUserCourseSettingsViewSet.as_view(), name='client_user_course_settings'),
])

# API CHAT
chat_patterns = ([
    path('chat/', ChatViewSet.as_view(), name='chat_list'),
    path('chat/<int:pk>/delete/', ChatDeleteView.as_view(), name='delete_chat'),
    path('message/', MessageViewSet.as_view(), name='message_list'),
    path('mass_message/', MassMessageView.as_view(), name='mass_message'),
    path('message/is_read/', UserMessageView.as_view({'post': 'post'}), name='message_is_read'),
    path('unread_message/', GetUnreadMessageCountView.as_view(), name='unread_message'),
    path('firebase/apikey/get/', GetFirebaseSettingsView.as_view(), name='get firebase_apikey'),
    path('firebase/apikey/change/', ChangeFirebaseSettingsViewSet.as_view({'put': 'update'}),
         name='change firebase_apikey'),
])

# API CURATOR
curator_patterns = ([
    path('ref/users/', curator_views.CuratorUsersListView.as_view(), name='ref_curator_users'),
    path('all_activity/', curator_views.CuratorUserAllActivityListView.as_view(), name='curator_all_activity'),
    path('users/', CuratorUserViewSet.as_view({'get': 'list'}), name='curator_users'),
    path('user/<int:pk>/progress/', CuratorUserProgressView.as_view(), name='curator_user_progress'),
    path('user_course_settings/', CuratorUserCourseSettingsViewSet.as_view(), name='user_course_settings'),
])

# API CONFERENCE
conference_patterns = ([
    path('apikey/get/', GetApiKeyView.as_view(), name='get conference_apikey'),
    path('apikey/change/', ChangeApiKeyViewSet.as_view({'put': 'update'}), name='change conference_apikey'),
])

# API QUICKLOGIN
quicklogin_patterns = ([
    path('', QuickloginViews.as_view(), name='get quick login'),
    path('change', ChangeQuickLogin.as_view(), name='change quick login settings')
])

# API NOTIFICATIONS
notifications_patterns = ([
    path('', MessageNotificationView.as_view(), name='get notifications list'),
    path('<int:pk>', MessageNotificationDetail.as_view(), name='update notification'),
])

urlpatterns = [
    path('token/', include(jwt_patterns)),
    path('users/', include(company_patterns)),
    path('user/', include(common_user_patterns)),
    path('courses/', include(courses_patterns)),
    path('chats/', include(chat_patterns)),

    path('client/courses/', include(client_courses_patterns)),
    path('client/users/', include(client_company_patterns)),
    path('client/testing/', include(client_testing_patterns)),

    path('curator/', include(curator_patterns)),
    path('time/', server_time, name='server_time'),
    path('register_new_user/', RegisterNewUser.as_view(), name='register_new_user'),

    path('conference/', include(conference_patterns)),
    path('quickauth/', include(quicklogin_patterns)),
    path('notifications/', include(notifications_patterns)),
]
