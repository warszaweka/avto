create or replace function "fillVendor"() returns void as $$
declare
  _titles text[] := array[
    'Volkswagen',
    'Renault',
    'Skoda',
    'Toyota',
    'Ford',
    'Opel',
    'Hyundai',
    'Mersedes-Benz',
    'Daewoo'
  ];
begin
  for _title_i in 1 .. array_upper(_titles, 1) loop
    if not exists (select id from vendor where title = _titles[_title_i]) then
      insert into vendor (title) values (_titles[_title_i]);
    end if;
  end loop;
end;
$$ language plpgsql;
select "fillVendor"();
