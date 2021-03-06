fs = 40100;
t = 0:1/fs:10/6000;
x1 = sawtooth(2*pi*6000*t);
x2 = square(2*pi*6000*t);
subplot(211),plot(t,x1), axis([0 10/6000 -1.2 1.2])
xlabel('Time (sec)');
ylabel('Amplitude');
title('Sawtooth Periodic Wave');
subplot(212)
plot(t,x2)
axis([0 0.002 -1.2 1.2]);
xlabel('Time (sec)');
ylabel('Amplitude');
title('Square Periodic Wave'); 