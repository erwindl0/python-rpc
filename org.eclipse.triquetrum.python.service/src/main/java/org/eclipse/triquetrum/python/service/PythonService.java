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
package org.eclipse.triquetrum.python.service;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.triquetrum.python.service.util.NetUtils;
import org.eclipse.triquetrum.python.service.util.cmdline.ManagedCommandline;
import org.eclipse.triquetrum.scisoft.analysis.rpc.AnalysisRpcClient;
import org.eclipse.triquetrum.scisoft.analysis.rpc.AnalysisRpcRemoteException;

/**
 * This class encapsulates a system command to python used with the RPC service. Minimized version of the org.dawnsci.python.rpc.PythonService.
 */
public class PythonService {

  public static final String PYTHON_DEBUG_PORT_PROP_NAME = "org.foobar.python.debug.port";
  public final static String PYTHON_FREE_PORT_PROP_NAME = "org.foobar.python.free.port";
  public final static String PYTHON_RPC_SERVICE_TIMEOUT_PROP_NAME = "org.foobar.python.timeout";
  public final static String SYSTEM_SCRIPTS_HOME = System.getProperty("org.foobar.python.scripts.system");

  private ManagedCommandline command;
  private AnalysisRpcClient client;
  private Thread stopThread;

  /**
   * Must use openConnection()
   */
  private PythonService() {

  }

  /**
   * Each call to this method starts a python process with a server waiting for commands. An RCP client is attached to it.
   *
   * @param command
   *          to start a python with numpy in. For instance 'python', 'python2.6', or the full path The port is started at 8613 and a free one is searched for.
   *          The property org.dawb.passerelle.actors.scripts.python.free.port many be used to change the start port if needed. This method also adds a shutdown
   *          hook to ensure that the service is stopped cleanly when the vm is shutdown. Calling the stop() method removes this shutdown hook.
   * @return
   */
  public static synchronized PythonService openConnection(final String pythonInterpreter) throws Exception {

    final PythonService service = new PythonService();

    // Find the location of python_service.py and
    // ensure org.eclipse.triquetrum.scisoft.python in PYTHONPATH
    final Map<String, String> env = new HashMap<String, String>(System.getenv());
    String pythonPath = env.get("PYTHONPATH");

    StringBuilder pyBuf;
    if (pythonPath == null) {
      pyBuf = new StringBuilder();
    } else {
      pyBuf = new StringBuilder(pythonPath);
      pyBuf.append(File.pathSeparatorChar);
    }
    final int port = NetUtils.getFreePort(getServiceStartPort());
    String script = SYSTEM_SCRIPTS_HOME + "/python_service_runscript.py";

    service.command = new ManagedCommandline();
    service.command.addArguments(new String[] { pythonInterpreter, "-u", script, String.valueOf(port), "-1" });

    env.put("PYTHONPATH", pyBuf.append(SYSTEM_SCRIPTS_HOME).toString());
    service.command.setEnv(env);

    // Currently log back python output directly to the log file.
    service.command.setStreamLogsToLogging(true);
    service.command.execute();

    service.stopThread = new Thread("Stop Python Service") {
      public void run() {
        service.stop();
      }
    };
    Runtime.getRuntime().addShutdownHook(service.stopThread);

    service.client = service.getActiveClient(port);

    return service;
  }

  /**
   * Tries to get a dir in the same place as the script, otherwise it tries to get a dir in the user home.
   *
   * @param scriptPath
   * @return
   */
  private static File getWorkingDir(final String scriptPath) {

    File path = null;
    try {
      final File dir = (new File(scriptPath)).getParentFile();
      path = getUniqueDir(dir, "python_tmp");
      if (!path.canWrite() || !path.isDirectory() || !canTouch(path)) {
        path = null;
      }
    } catch (Throwable ne) {
      path = null;
    }

    if (path == null) {
      File home = new File(System.getProperty("user.home") + "/.dawn/");
      home.mkdirs();
      path = getUniqueDir(home, "python_tmp");
    }

    return path;

  }

  private static File getUniqueDir(File dir, String name) {

    int i = 1;
    File ret = new File(dir, name + i);
    while (ret.exists()) {
      if (ret.list() == null || ret.list().length < 1)
        break; // Use the same empty one.
      ++i;
      ret = new File(dir, name + i);
    }
    ret.mkdirs();
    return ret;
  }

  private static boolean canTouch(File path) {
    try {
      path.mkdirs();
      File touch = new File(path, "touch");
      touch.createNewFile();
      touch.delete();
    } catch (Throwable ne) {
      return false;
    }
    return true;
  }

  /**
   * This call opens a client to the service already running. If you want you can run the python_serice.py in pydev then debug the commands as they come it. Use
   * this method to get the PythonService Java side in that case. It will look for the running RPC service on the port passed in and allow commands to be run
   * and debugged.
   *
   * @param port
   * @return
   * @throws Exception
   */
  public static PythonService openClient(final int port) throws Exception {

    final PythonService service = new PythonService();

    service.client = service.getActiveClient(port);

    return service;
  }

  /**
   * Tries to connect to the service, only returning when connected. This is more reliable than waiting for a given time.
   *
   * @param port
   * @return
   * @throws InterruptedException
   */
  private AnalysisRpcClient getActiveClient(int port) throws Exception {

    if (!isRunning())
      throw new Exception("The remote python process did not start!");

    int count = 0;
    final int time = System.getProperty(PYTHON_RPC_SERVICE_TIMEOUT_PROP_NAME) != null
        ? Integer.parseInt(System.getProperty(PYTHON_RPC_SERVICE_TIMEOUT_PROP_NAME)) : 5000;

    while (count <= time) {
      try {
        final AnalysisRpcClient client = new AnalysisRpcClient(port);
        final Object active = client.request("isActive", new Object[] { "unused" }); // Calls the method 'run' in the script with the arguments
        if ((((Boolean) active)).booleanValue())
          return client;
        Thread.sleep(100);
        count += 100;
        continue;
      } catch (Exception ne) {
        count += 100;
        Thread.sleep(100);
        continue;
      }
    }
    throw new Exception("RPC connect to python timed out after " + time + "ms! Are you sure the python server is going?");
  }

  /**
   * Will be null when openClient(port) is used.
   *
   * @return
   */
  public ManagedCommandline getCommand() {
    return command;
  }

  public AnalysisRpcClient getClient() {
    return client;
  }

  public void stop() {
    if (command == null)
      return;
    if (command.getProcess() == null)
      return;
    command.getProcess().destroy();
    if (stopThread != null) {
      try {
        Runtime.getRuntime().removeShutdownHook(stopThread);
      } catch (Throwable ne) {
        // We try to remove it but errors are not required if we fail because this method may
        // be called during shutdown, when it will.
      }
      stopThread = null;
    }

  }

  public boolean isRunning() {
    if (command == null)
      return true; // Probably in debug mode
    return !command.hasTerminated();
  }

  /**
   * Convenience method for calling
   *
   * @param methodName
   * @param arguments
   * @return
   * @throws Exception
   */
  @SuppressWarnings("unchecked")
  public Map<String, ? extends Object> runScript(String scriptFullPath, Map<String, ?> data) throws Exception {

    final File dir = getWorkingDir(scriptFullPath);
    command.setWorkingDir(dir);
    final List<String> additionalPaths = new ArrayList<String>(1);
    additionalPaths.add(new File(scriptFullPath).getParent().toString());
    if (System.getenv("PYTHONPATH") != null) {
      additionalPaths.addAll(Arrays.asList(System.getenv("PYTHONPATH").split(File.pathSeparator)));
    }

    final Object out = client.request("runScript", new Object[] { scriptFullPath, data });

    if (dir.exists() && (dir.list() == null || dir.list().length < 1)) {
      dir.delete();
    }

    // Calls the method 'runScript' in the script with the arguments
    return (Map<String, ? extends Object>) out;
  }

  public static int getDebugPort() {
    int port = 8613;
    if (System.getProperty(PYTHON_DEBUG_PORT_PROP_NAME) != null) {
      // In an emergency allow the port to be changed for the debug session.
      port = Integer.parseInt(System.getProperty(PYTHON_DEBUG_PORT_PROP_NAME));
    }
    return port;
  }

  /**
   * Returns the port used to start the search for a free port in non-debug mode
   *
   * @return
   */
  private static int getServiceStartPort() {
    int port = 8613;
    if (System.getProperty(PYTHON_FREE_PORT_PROP_NAME) != null) {
      // In an emergency allow the port to be changed for the debug session.
      port = Integer.parseInt(System.getProperty(PYTHON_FREE_PORT_PROP_NAME));
    }
    return port;
  }

  /**
   * Formats a remote exception to limit the Python code that was not "users" code.
   *
   * @param e
   *          Remote Exception to format
   * @return a Python style exception format
   */
  public String formatException(AnalysisRpcRemoteException e) {
    return e.getPythonFormattedStackTrace("python_service.py");
  }

}
