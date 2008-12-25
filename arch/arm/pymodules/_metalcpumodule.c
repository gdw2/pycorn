/*
 * Copyright 2008 Torne Wuff
 *
 * This file is part of Pycorn.
 *
 * Pycorn is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

#include <Python.h>
#include "_metalcpu_coproc.h"

extern unsigned metalcpu_coprocread_asm(int regindex);
extern unsigned metalcpu_coprocwrite_asm(int regindex, unsigned value);

static PyObject *
metalcpu_coprocread(PyObject *self, PyObject *args)
{
    int regindex;
    unsigned val;

    if (!PyArg_ParseTuple(args, "i", &regindex))
        return NULL;
    if (regindex < 0 || regindex >= COPROCREAD_REGS)
    {
        PyErr_SetString(PyExc_IndexError, "register index out of range");
        return NULL;
    }
    val = metalcpu_coprocread_asm(regindex);
    return Py_BuildValue("I", val);
}

static PyObject *
metalcpu_coprocwrite(PyObject *self, PyObject *args)
{
    int regindex;
    unsigned val;

    if (!PyArg_ParseTuple(args, "iI", &regindex, &val))
        return NULL;
    if (regindex < 0 || regindex >= COPROCWRITE_REGS)
    {
        PyErr_SetString(PyExc_IndexError, "register index out of range");
        return NULL;
    }
    metalcpu_coprocwrite_asm(regindex, val);
    Py_RETURN_NONE;
}

static const PyMethodDef MetalCpuMethods[] = {
    {"coproc_read", metalcpu_coprocread, METH_VARARGS, "Read a 32-bit word from a coprocessor register."},
    {"coproc_write", metalcpu_coprocwrite, METH_VARARGS, "Write a 32-bit word to a coprocessor register."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initmetalcpu(void)
{
    PyObject *m;

    m = Py_InitModule("_metalcpu", MetalCpuMethods);
    if (m == NULL)
        return;
}

__attribute__((constructor)) void appendmetalcpu()
{
    PyImport_AppendInittab("_metalcpu", initmetalcpu);
}