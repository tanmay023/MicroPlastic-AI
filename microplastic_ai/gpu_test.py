import torch

print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

x = torch.randn(5000, 5000).cuda()
y = torch.randn(5000, 5000).cuda()

z = torch.matmul(x, y)

print(z.shape)
print("GPU Working Successfully")