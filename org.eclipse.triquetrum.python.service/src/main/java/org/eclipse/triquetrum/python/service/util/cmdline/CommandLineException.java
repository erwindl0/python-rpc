/*******************************************************************************
 * Copyright (c) 2014, 2016  Diamond Light Source Ltd., 
 *                          Kichwa Coders & iSencia Belgium NV.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    DLS, Kichwa Coders - initial API and implementation and/or initial documentation
 *    Erwin De Ley - extraction from DAWN to ease reuse in other contexts
 *******************************************************************************/
package org.eclipse.triquetrum.python.service.util.cmdline;

/**
 * @author wim
 */
public class CommandLineException extends Exception {

  private static final long serialVersionUID = 9175542101325245662L;

  public CommandLineException(String message) {
    super(message);
  }
}
