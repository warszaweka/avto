create or replace function "fillSpec"() returns void as $$
declare
  _titles text[] := array[
    'Техническое обслуживание',
    'Ходовая и рулевая',
    'Система охлаждения и обогрева',
    'Кондиционер',
    'Двигатель',
    'Электрика',
    'Выхлопная система',
    'Коробка переключения',
    'Кузов',
    'Другое',
    'Нужна диагностика',
    'Малярные услуги',
    'Шиномонтаж',
    'ГБО',
    'Замена стекла',
    'Освещение',
    'Тюнинг'
  ];
begin
  for _title_i in 1 .. array_upper(_titles, 1) loop
    if not exists (select id from spec where title = _titles[_title_i]) then
      insert into spec (title) values (_titles[_title_i]);
    end if;
  end loop;
end;
$$ language plpgsql;
select "fillSpec"();
