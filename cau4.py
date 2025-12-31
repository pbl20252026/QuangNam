def square(n):
    return n * n

numbers = [1, 2, 3, 4]

# map trả về một iterator , nên ta thường ép kiểu về list để xem kết quả
result = map(str, numbers) 

print(list(result)) # Kết quả: [1, 4, 9, 16]
print ('test branch nheee')