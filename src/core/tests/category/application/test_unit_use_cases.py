# from typing import Optional
# from datetime import datetime

# from core.category.application.use_cases import CategoryOutput, CreateCategoryUseCase
# from core.category.domain.entities import Category


# class TestCategoryOutput:

#     def test_fields(self):
#         assert CategoryOutput.__annotations__, {
#             'id': str,
#             'name': str,
#             'description': Optional[str],
#             'is_active': bool,
#             'created_at': datetime
#         }

#     def test_from_entity(self):
#         category = Category.fake().a_category().build()
#         output = CategoryOutput.from_entity(category)
#         assert output.id == category.category_id.id
#         assert output.name == category.name
#         assert output.description == category.description
#         assert output.is_active == category.is_active
#         assert output.created_at == category.created_at

# class TestCreateCategoryUseCaseUnit:

#     use_case: CreateCategoryUseCase
#     category_repo: CategoryIn

#     def setUp(self) -> None:
#         self.category_repo = CategoryInMemoryRepository()
#         self.use_case = CreateCategoryUseCase(self.category_repo)

#     def test_if_instance_a_use_case(self):
#         self.assertIsInstance(self.use_case, UseCase)

#     def test_input(self):
#         self.assertEqual(CreateCategoryUseCase.Input.__annotations__, {
#             'name': str,
#             'description': Optional[str],
#             'is_active': Optional[bool],
#         })
#         # pylint: disable=no-member
#         description_field = CreateCategoryUseCase.Input.__dataclass_fields__[
#             'description']
#         self.assertEqual(description_field.default,
#                          Category.get_field('description').default)

#         is_active_field = CreateCategoryUseCase.Input.__dataclass_fields__[
#             'is_active']
#         self.assertEqual(is_active_field.default,
#                          Category.get_field('is_active').default)

#     def test_output(self):
#         self.assertTrue(
#             issubclass(
#                 CreateCategoryUseCase.Output,
#                 CategoryOutput
#             )
#         )

#     def test_execute(self):
#         with patch.object(
#             self.category_repo,
#             'insert',
#             wraps=self.category_repo.insert
#         ) as spy_insert:
#             input_param = CreateCategoryUseCase.Input(name='Movie')
#             output = self.use_case.execute(input_param)
#             spy_insert.assert_called_once()
#             self.assertEqual(output, CreateCategoryUseCase.Output(
#                 id=self.category_repo.items[0].id,
#                 name='Movie',
#                 description=None,
#                 is_active=True,
#                 created_at=self.category_repo.items[0].created_at
#             ))

#         input_param = CreateCategoryUseCase.Input(
#             name='Movie', description='some description', is_active=False)
#         output = self.use_case.execute(input_param)
#         self.assertEqual(output, CreateCategoryUseCase.Output(
#             id=self.category_repo.items[1].id,
#             name='Movie',
#             description='some description',
#             is_active=False,
#             created_at=self.category_repo.items[1].created_at
#         ))

#         input_param = CreateCategoryUseCase.Input(
#             name='Movie', description='some description', is_active=True)
#         output = self.use_case.execute(input_param)
#         self.assertEqual(output, CreateCategoryUseCase.Output(
#             id=self.category_repo.items[2].id,
#             name='Movie',
#             description='some description',
#             is_active=True,
#             created_at=self.category_repo.items[2].created_at
#         ))