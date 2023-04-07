/**
 * Функция преобразует объект в FormData
 * @param data объект
 * @returns объект FormData
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function toFormData(data: Record<any, any>): FormData {
  const formData = new FormData();

  Object.entries(data).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      formData.append(key, value);
    }
  });

  return formData;
}
