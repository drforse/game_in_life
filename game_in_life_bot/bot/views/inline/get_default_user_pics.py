from aiogram_oop_framework.views import InlineQueryView
from aiogram.types import InlineQuery, InlineQueryResultCachedPhoto
from aiogram.dispatcher import FSMContext

from ....models import DefaultUserpicsModel


class GetDefaultUserPics(InlineQueryView):
    custom_filters = [lambda q: q.query == 'default userpics']
    state = lambda: '*'

    @classmethod
    async def execute(cls, q: InlineQuery, state: FSMContext):
        default_user_photos = []
        photo_ids = DefaultUserpicsModel.get().photo_ids.copy()
        user_profile_photos = await q.from_user.get_profile_photos()
        photo_ids += [ph[-1].file_id for ph in user_profile_photos.photos]
        for num, photo_id in enumerate(photo_ids):
            photo = InlineQueryResultCachedPhoto(id=str(num),
                                                 photo_file_id=photo_id)
            default_user_photos.append(photo)

        await q.answer(default_user_photos)
