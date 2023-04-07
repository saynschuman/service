/**
 * Возвращает уникальные значения массива
 * @param value значение элемента массива
 * @param index порядковый номер элемента в массиве
 * @param self начальный массив
 * @returns массив с уникальными значениями без повторяющихся элементов
 */
export function onlyUnique<T extends unknown[]>(
  value: number | string,
  index: number,
  self: T,
): boolean {
  return self.indexOf(value) === index;
}
