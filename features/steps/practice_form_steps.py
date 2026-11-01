from behave import given, when, then


@given("открыта форма регистрации студента")
def open_form(context):
    context.form.open_form()


@when('пользователь вводит имя "{first}" фамилию "{last}" и телефон "{mobile}"')
def fill(context, first, last, mobile):
    context.form.fill_required(first,last,mobile)


@when("отправляет форму")
def submit(context):
    context.form.submit()


@then("отображаются данные зарегистрированного студента")
def accepted(context):
    context.form.assert_submitted()
    context.form.assert_result("Student Name","Вадим Боттер")
    context.form.assert_result("Mobile","9991234567")


@then("форма отклоняет введённые данные")
def rejected(context):
    context.form.assert_rejected()
