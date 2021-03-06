%coeffs = int32([1427,-154,416,-517,-134,-281,-54,136,140,131,116,-206])
%coeffs = int32([-1664 306 339])
block = 9
m = 12

a = sum(1:m - 1)
b = sum(1:m)
all_coeffs = load('ld_coefficients.txt');
all_coeffs = all_coeffs(a + 1:b)

coeffs = int32(fliplr(all_coeffs'))
order = max(size(coeffs))

data = dlmread('Pavane16Blocks.txt');

data = int32(data(block*4096 + 1:(block + 1)*4096));
filtered_tb = load('residual_pipelined.txt');

residual = int32(zeros(1, 4096));
for i = order + 1:4096
    Sum = 0;
    for j = 1:order
        Sum = Sum + data(i - j)*coeffs(j);
    end
    
    residual(i) = data(i) - Sum/1024;
end

filtered_tb = int32([zeros(1,order), filtered_tb(1:4096-order)']);
%filtered_tb = circshift(filtered_tb, [0 -1]);
plot(1:4096, residual, 'b+', 1:4096, filtered_tb, 'ro');
legend('Matlab','Hardware')
%
figure
plot(residual - filtered_tb, 'g.')