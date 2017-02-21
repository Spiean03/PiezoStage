%duration [s]
T=10;
%sample rate [Hz] Supported by SoundCard (16000,48000,96000,192000)
Fs = 48000;
%samples
N = T*Fs;
%samples vector
t = 0 : 1/Fs : T;
%Frequency [Hz]
Fn = 1000;
%Signal
y = sin(Fn*2*pi*t);
plot(t,y);
%Play sound
sound(y,Fs);
audiowrite('sine.wav',y,Fs);
%%
%duration [s]
T=0.1;
%sample rate [Hz] Supported by SoundCard (16000,48000,96000,192000)
Fs = 48000;
%samples
N = T*Fs;
%samples vector
t = 0 : 1/Fs : T;
%Frequency [Hz]
Fn = 1000;
%Signal
y = sawtooth(Fn*2*pi*t);
plot(t,y);
%Play sound
sound(y,Fs);
audiowrite('sawtooth_100_10times.wav',y,Fs);
%%
%duration [s]
T=0.1;
%sample rate [Hz] Supported by SoundCard (16000,48000,96000,192000)
Fs = 48000;
%samples
N = T*Fs;
%samples vector
t = 0 : 1/Fs : T;
%Frequency [Hz]
Fn = 1000;
%Signal
y = sawtooth(-Fn*2*pi*t);
plot(t,y);
%Play sound
sound(y,Fs);
audiowrite('sawtooth_100_minus.wav',y,Fs);
%%
%duration [s]
T=0.01;
%sample rate [Hz] Supported by SoundCard (16000,48000,96000,192000)
Fs = 48000;
%samples
N = T*Fs;
%samples vector
t = 0 : 1/Fs : T;
%Frequency [Hz]
Fn = 1000;
%Signal
y = sawtooth(Fn*2*pi*t);
plot(t,y);
%Play sound
%sound(y,Fs);
audiowrite('sawtooth_10.wav',y,Fs);
%%
%duration [s]
T=0.01;
%sample rate [Hz] Supported by SoundCard (16000,48000,96000,192000)
Fs = 48000;
%samples
N = T*Fs;
%samples vector
t = 0 : 1/Fs : T;
%Frequency [Hz]
Fn = 1000;
%Signal
y = sawtooth(-Fn*2*pi*t);
plot(t,y);
%Play sound
%sound(y,Fs);
audiowrite('sawtooth_10_minus.wav',y,Fs);
%%

t  = [ 0 : 1 : 10000];           % Time Samples
f  = 1000;                       % Input Signal Frequency
Fs = 44100;                     % Sampling Frequency
data = sin(2*pi*f/Fs*t)';        % Generate Sine Wave
wavplay(data,Fs)  
audiowrite('test.wav',y,Fs);
