# ARM64 basis code injection - full description below

Script where you can inject **JMP** instruction into C program's memory on **ARM64** basis architecture.

***Our goal is to add JUMP instruction after executed func(&val), due to make a loop of main function program that causing it doesn't terminate the program.***

Then we need two things to let it works:
- **Address of place of its process where we inject JMP**
- **Address of starting main function, the place where we jump in** 

<br>Our program that we do inject on is relatively simple:

```
#include <stdio.h>

void func(char* val) {
	printf("%d\n", *val);
}

int main(void) {
	 char val;
	 fread(&val, 1, 1, stdin);
	 func(&val);
	 
	 return 0;	
}

```
It takes one character on input and it prints out its character's ASCII code.

<br>We can use objdump program to read where func(&val) ends up its execution, so we can use:

**On Unix based systems, you can use \`pidof main` from bash**
> sudo objdump /proc/\`pidof main`/exe -dw | grep -a -A 30 \"<main\>"

<br>**On Windows systems use getpid.py python script to get PID of program \`python getpid.py`**
> sudo objdump /proc/\`python getpid.py`/exe -dw | grep -a -A 30 \"<main\>"

```
 954:	97ffff8f 	bl	790 <fread@plt>
 958:	91001fe0 	add	x0, sp, #0x7
 95c:	97ffffe3 	bl	8e8 <func>
 960:	52800000 	mov	w0, #0x0                   	// #0
 964:	2a0003e1 	mov	w1, w0
 968:	f00000e0 	adrp	x0, 1f000 <__abi_tag+0x1e52c>

```
We can see interesting address `0x960` where we can inject JMP instruction (Operating principle is the same on **x86_64** architecture).

```
0000000000000918 <main>:
 918:	d10083ff 	sub	sp, sp, #0x20
 91c:	a9017bfd 	stp	x29, x30, [sp, #16]
 920:	910043fd 	add	x29, sp, #0x10
```
And we know also that the main function is starting from `0x918`, so its the point where we want to jump.

<br>The last address we need to know is **Base Address**, that's why we know where our **program** is starting in memory.
It is depending from executable marking if program is marked as `ET_EXEC`, it means that **Base Address** of its doesn't change.
If the program is marked as `ET_DYN`, its causing that each program execution will restart **Base Address** of its program in memory.
Fortunately, we don't need to worry about **Base Address**, because I have included `getBaseAddessFromMapsFile()` which getting this address.

Further more we can execute procwrite.py to modificate our program behaviour:
- Firstly, we had to execute main program
- Then we execute procwrite.py script
- We check out the memory of program in runtime

<br>How we can check it out if it works?
We can use GNU Debugger to disassemble \<main> function, so let's execute the following command:
> gdb -p \`pidof main`
And now we see that its program's memory has been modificated:
```
   0x0000ac89c7670954 <+60>:	bl	0xac89c7670790 <fread@plt>
   0x0000ac89c7670958 <+64>:	add	x0, sp, #0x7
   0x0000ac89c767095c <+68>:	bl	0xac89c76708e8 <func>
   0x0000ac89c7670960 <+72>:	ldr	x16, 0xac89c7670968 <main+80>
   0x0000ac89c7670964 <+76>:	br	x16
   0x0000ac89c7670968 <+80>:	.inst	0xc7670918 ; undefined
   0x0000ac89c767096c <+84>:	udf	#44169
   0x0000ac89c7670970 <+88>:	ldr	x3, [sp, #8]
   0x0000ac89c7670974 <+92>:	ldr	x2, [x0]
   0x0000ac89c7670978 <+96>:	subs	x3, x3, x2
```
We see that under `0x960` address, there is written an address +8 bytes to ldr registry.
Next line we have br that makes jump to the `0xc7670918`.

## Thank you for reading this laboratory knowledge:
I was basing on knowledge from the book "Practical Reverse Engineering - Gynvael Coldwind".

